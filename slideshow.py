#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as LOGGER
import tomlkit.toml_document
import tomlkit.toml_file
import imgutils as imgutils
import time
import plugins
import slideshow_hookimpl
import pluginmanager_hookimpl
from os import path as osp
import os, sys
from PIL import Image
from dynaconf import Dynaconf, loaders
from dynaconf.utils.boxing import DynaBox
import plugins.hookspecs as hookspecs
from enum import IntEnum
import threading
import remi
import random
import tomlkit
import tempfile

class SlideShow:
    class Stage(IntEnum):
        LOAD = 0
        RESIZE = 1
        SHOW = 2
        IDLE = 3
        def nextStage(self):
            newStage = SlideShow.Stage((self+1)%len(SlideShow.Stage))
            LOGGER.debug(f"New Stage: {newStage.name}")
            return newStage

    uploadPath : str  = tempfile.gettempdir() # path for uplading files. For RPI should be in temp because we're RO
    loadedByPlugin : str = None # plugin which loaded the active image            
    image : Image = None # current image
    resizedImage : Image = None # image after resize stage
    loadedImage : Image = None # image as it has been loaded
    brightnessMask : int = (0,0,0,0) #Initial Brightness is 100% with no color modification.
    delay : float = 60.0 # Delay between photos in seconds
    imageInfo : dict = None #information about currently shown picture
    pm : plugins.FramePluginManager = None
    cfg : Dynaconf = None
    quit : bool = False # quit requested from a plugin
    paused : bool = False # paused via remote
    forceLoad : bool = False # load request via remote 
    idleIter : int = 0 # Idle iterator. Set in Show() because plugins may change it
    stage : Stage = Stage.LOAD # Current stage. Stages are : 0 = load, 1 = resize, 2 = show, 3 = idle
    cond : threading.Condition #notifycation for idle sleep 
    frameSize : tuple[int,int] = (1024,800) # Frame size
    shuthown : bool = False # System should be shut down after the app quits
    reboot : bool = False # System should be rebooted after the app quits
    activeLoadersCount : int = 0 # count of loader plugins. Set in stageLoad. Used for determining if idleIter should be incremented
    @property
    def brightness(self):
        return 255-self.brightnessMask[3]
    def quitApp(self, quit = True, shutdown = False, reboot = False):
        self.quit = quit
        self.shutdown = shutdown
        self.reboot = reboot

    def __init__(self):
        self.cond = threading.Condition()

    def createAPI(self):
        self.pm.hook.setAPI(app=self) # set REST API (FastAPI) here
        

    def createRemote(self) -> list[list[remi.Widget]]:
        """Called from remote (if exists). For setting remote UI in plugins"""
        hookImpls = self.pm.hook.setRemote.get_hookimpls()
        widgets = []
        for hookImpl in hookImpls:
            widgets.append((hookImpl.plugin_name,
                            self.pm.getFancyName(hookImpl.plugin, False),
                             hookImpl.function(app=self))) #call plugins
        return widgets         
    def get_plugin_manager(self):
        self.pm = plugins.FramePluginManager("slideshow")
        self.pm.add_hookspecs(hookspecs)
        self.pm.register(slideshow_hookimpl)
        self.pm.register(pluginmanager_hookimpl)
        defaultConfig = {"ACTIVE" : ["DUMMYFRAME","REMOTE","NIGHTMODE","CLOCKS","URLLOADER"]}
        self.loadCfg("PLUGINS", defaultConfig) #load the real config and merge it with default values
        self.pm.loadAllPluginsFromDir(active=self.cfg.PLUGINS.ACTIVE)
        
        
    def registerPlugin(self,pluginName : str):
        plugin = self.pm.getAvailablePlugin(pluginName)
        if plugin:
            self.pm.register(plugin)
            # call startup
            if hasattr(plugin, "loadCfg"):
                plugin.loadCfg(self)
            if hasattr(plugin, "startup"):
                plugin.startup(self)
            stage = self.Stage.LOAD
            if hasattr(self, "remote") and hasattr(plugin, "setRemote"):
                self.remote.serverApp.addPluginContainer(plugin.PLUGIN_NAME,
                    self.pm.getFancyName(plugin, False),
                    plugin.setRemote(app=self)) #call plugin
            if hasattr(self, "api") and hasattr(plugin, "setAPI"):
                plugin.setAPI(self)

            if hasattr(plugin, "PLUGIN_CLASS"):
                if plugin.PLUGIN_CLASS == "LOADER":
                    stage = None
            self.setStage(stage) #force reload
    
    def unregisterPlugin(self, plugin : str):
        # unchecked - clean and deregister the plugin
        pluginName : str = plugin.PLUGIN_NAME
        if hasattr(plugin, "exit"):
            plugin.exit(app=self)
        self.pm.unregister(plugin)
        self.setStage(self.Stage.LOAD)
        if hasattr(self, "remote"):
            self.remote.serverApp.removePluginContainer(pluginName)

 
    def fileUpload(self,filename : str, plugin_name : str):
        """
        Called from plugins when file was uploaded. Forces show the file
        """
        fullPath : str = os.path.join(self.uploadPath, filename)
        if self.stageLoad(fullPath): #lazy !!!
            self.loadedByPlugin = plugin_name
            self.setStage(self.Stage.LOAD)
        try:
            os.remove(fullPath) # remove downloaded file
        except OSError as e:
            LOGGER.error(f"File couldn't be removed {fullPath} {e}")
            
        


    def sendToFrame(self):
        """Shows the image at defined frames"""
        self.imageBeforeEffects = self.image
        self.pm.hook.imageChangeBeforeEffects(app=self) # call effect plugins here (for nightmode etc.)
        if (self.image.size != tuple(self.frameSize)): # final size check. Wrong size can break the frame
            self.image = imgutils.resize_and_centerImg(self.image, self.frameSize)
        ret : list[bool] = self.pm.hook.showImage(app=self)
        if ret and any(ret): 
            return True
    
    def setBrightness(self, brightness : int , color : tuple[int,int,int] = None):
        brMask : int = 255 - brightness
        if not color:
            # set color from current brightness
            color = (self.brightnessMask[:3])
        self.brightnessMask = (color[0],color[1],color[2],brMask)
        if self.brightnessMask == (0,0,0,0): #ignore for default situation
            ...
        else:
            image = Image.new('RGBA', self.frameSize , self.brightnessMask)
            self.image = imgutils.pasteImage(bgImage=self.image, fgImage=image)
        self.pm.hook.brightnessChangeAfter(app=self, brightness=brightness)

        
    def stageLoad(self, buffer : bytes = None) -> bool:
        """loads a new image. Buffer is here to force a specific image from plugins"""
        self.idleIter = 0
        self.loadedByPlugin = None
        hookImpls = self.pm.hook.load.get_hookimpls()
        self.activeLoadersCount = len(hookImpls)
        if not buffer:
            buffers = []
            for hookImpl in hookImpls:
                buffers.append((hookImpl.plugin,hookImpl.function(app=self))) #call plugins
            buffers = list(filter(lambda b: b[1], buffers)) #filter out invalid results
            if buffers:
                if len(buffers)>1:
                    plugin,buffer = random.choice(buffers) # randomize the result
                else:
                    plugin,buffer = buffers[0] # return first buffer
                self.loadedByPlugin = plugin.PLUGIN_NAME
            
        if buffer:
            self.loadedImage = imgutils.bytes2img(buffer)
            if self.loadedImage:
                self.loadedImage = imgutils.exifTranspose(self.loadedImage) #rotate the image
                self.forceLoad = False #new image has been loaded or it failed
                self.pm.hook.loadAfter(app=self)
                return True #must returns True if success because of plugins
        #show last downloaded image. At least show something
        self.image = self.loadedImage

        if not self.image:
            try:
                #data = imgutils.loadFile(osp.join(osp.realpath(osp.dirname(__file__)),"res","monoscope.png"))
                self.image = imgutils.bytes2img(osp.join(osp.realpath(osp.dirname(__file__)),"res","monoscope.png"))
            except:
                self.image = Image.new('RGBA', self.cfg.FRAME.IMG_SIZE, (0, 0, 0, 0)) #black screen when nothing has been loaded and there's no image at all
            self.loadedImage = self.image
        return True

    def stageResize(self):
        """Resize to fit the frame"""
        if self.image:
            ret = self.pm.hook.ResizeBefore(app=self)
            if ret and any(ret): #at least one ResizeBefore returned True
                self.resizedImage = self.image
            else:
                self.resizedImage = imgutils.resize_and_centerImg(self.image, self.frameSize)
            self.image = self.resizedImage
            self.pm.hook.ResizeAfter(app=self)

    def stageShow(self):
        if self.image:
            self.pm.hook.imageChangeBefore(app=self)
            self.setBrightness(self.brightness)
            if self.sendToFrame():
                self.pm.hook.imageChangeAfter(app=self)
                return True
    
    def stageIdle(self):
        """Calls do() in plugins"""
        wait = 1 # wait 1s
        while (self.idleIter < self.delay or self.paused) and self.stage == self.Stage.IDLE:
            if not self.paused and self.activeLoadersCount:
                self.idleIter += wait
            start = time.time()
            self.pm.hook.do(app=self) # call plugins
            delta = time.time() - start # measure time lose in plugins
            waitD = wait - delta
            if self.quit: return
            if self.forceLoad: 
                self.idleIter = self.delay # force end of the cycle
                return
            if waitD > 0:
                with self.cond:
                    self.cond.wait(waitD)

    def setStage(self, stage : int ):
        """For calling from plugins. Sets correct image for the stage"""
        if stage == None:
            self.stage = None
        else:    
            if stage == self.Stage.RESIZE:
                self.image = self.loadedImage
            if stage == self.Stage.SHOW:
                self.image = self.resizedImage
            self.stage = self.Stage(stage)
        
        with self.cond: 
            self.cond.notify_all() #inform idle sleep if the stage change request was started from a different thread

        if self.stage:
            LOGGER.debug(f"New stage SET {self.stage.name}")

    def stages(self):
        """stage manager. Route is: load -> resize -> show -> idle"""
        while not self.quit:
            if self.stage == self.Stage.LOAD or self.stage == None:
                if self.stage == None:
                    self.stage = self.Stage.LOAD
                if not self.stageLoad():
                    LOGGER.error("Image wasn't loaded")
                    time.sleep(1)
                    self.idleIter = 0
                    self.stage = self.Stage.SHOW #go directly to idle

            elif self.stage == self.Stage.RESIZE:
                self.stageResize()
            elif self.stage == self.Stage.SHOW:
                if not self.stageShow(): 
                    time.sleep(10) #Display disconnected, not in monitor mode etc.
            elif self.stage == self.Stage.IDLE:
                self.stageIdle()
            if self.stage != None:
                self.setStage(self.stage.nextStage())

    def updateToml(self, data : DynaBox):
        """
        Updates the toml file with new data. 
        Original dynaconf.merge() can't be used here because it clears dynaconf_merge flag
        """
        filename=osp.join(self.cfg.root_path_for_dynaconf,"settings.local.toml")
        file :  tomlkit.toml_file.TOMLFile = tomlkit.toml_file.TOMLFile(filename)
        try:
            doc : tomlkit.toml_document.TOMLDocument = file.read()
        except FileNotFoundError:
            doc = tomlkit.toml_document.TOMLDocument()
        data = loaders.toml_loader.encode_nulls(data)
        
        doc.update(data)
        file.write(doc)

    def saveCfg(self, pluginName : str, data, merge = False):
        """
        Called from plugins. Saves the config to the toml file
        """
        
        dm = {"dynaconf_merge": merge}
        data.update(dm)
        dbox = DynaBox({pluginName : data})
        self.updateToml(dbox)

    def loadCfg(self, section : str, data : dict):
        """
        Called from plugins. Loads the config
        """
        setattr(self.cfg,section, self.cfg.get(section,data))
        # Workaround for dynaconf merge issue
        for key in data.keys():
            if key not in self.cfg[section]:
                self.cfg[section][key] = data[key]

    def saveCfgAll(self):
        """
        Saves all active plugin configs
        """
        self.pm.hook.saveCfg(app=self) #save current plugins config.
        
    def run(self, cfg : Dynaconf ) -> int:
        self.cfg = cfg
        self.frameSize = self.cfg.FRAME.IMG_SIZE
        self.get_plugin_manager()
        self.pm.hook.loadCfg(app=self) #loads defaults
        self.pm.hook.startup(app=self)
        try:
            self.stages()
        except KeyboardInterrupt:
            LOGGER.info("Interrupted")
        self.pm.hook.exit(app=self)
        if self.reboot:
            LOGGER.info("System Reboot")
            os.system('sudo shutdown -r now')
        if self.shutdown:
            LOGGER.info("System Shutdown")
            os.system('sudo shutdown -h now')
        return os.EX_OK
        
slideShow : SlideShow = None
if __name__ == '__main__':
    settings = Dynaconf(
        envvar_prefix="FRAME",
        root_path=osp.realpath(osp.dirname(__file__)),
        settings_files=['settings.toml','.secrets.toml']
        )
    loglevel = settings.FRAME.LOGLEVEL if hasattr(settings,"FRAME") and hasattr(settings.FRAME, "LOGLEVEL") else "INFO"
    LOGGER.basicConfig(level=loglevel, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
    slideShow = SlideShow()
    ex = slideShow.run(settings)
    sys.exit(ex) 
