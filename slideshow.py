#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as LOGGER
import imgutils as imgutils
import time
import plugins
from os import path as osp
from PIL import Image
from dynaconf import Dynaconf,loaders
from dynaconf.utils.boxing import DynaBox
import plugins.hookspecs as hookspecs
from enum import IntEnum
import threading
import remi

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
            
    image : Image = None # current image
    loadedImage : Image = None # image as it has been loaded
    imgLoader = None # active loader 
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
    remotelyUploaded : bool = False # The picture has been uploaded remotely via RC. Info for plugins
    cond : threading.Condition #notify for idle sleep 
    @property
    def brightness(self):
        return 255-self.brightnessMask[3]
    def quitApp(self, quit = True):
        self.quit = quit

    def __init__(self):
        self.cond = threading.Condition()
    
    def createRemote(self) -> list[list[remi.Widget]]:
        """Called from remote (if exists). For setting remote UI in plugins"""
        widgets = self.pm.hook.setRemote(app=self) #call plugins
        return widgets

    def idle(self):
        """Calls do() in plugins"""
        wait = 1 # wait 1s
        while (self.idleIter < self.delay or self.paused) and self.stage == self.Stage.IDLE:
            self.idleIter += wait
            start = time.time()
            self.pm.hook.do(app=self) #call plugins
            delta = time.time() - start #measure time lost in plugins
            waitD = wait - delta
            if self.quit: return
            if self.forceLoad: return
            if waitD > 0:
                with self.cond:
                    self.cond.wait(waitD)
            
    def get_plugin_manager(self):
        self.pm = plugins.FramePluginManager("slideshow")
        self.pm.add_hookspecs(hookspecs)
        self.pm.load_all_plugins(self.cfg.PLUGINS.ACTIVE)
        
        
    def sendToFrame(self):
        """Shows the image at defined frames"""
        self.imageBeforeEffects = self.image
        self.pm.hook.imageChangeBeforeEffects(app=self) # call effect plugins here (for nightmode etc.)
        if (self.image.size != tuple(self.cfg.FRAME.IMG_SIZE)): # final size check. Wrong size can break the frame
            self.image = imgutils.resize_and_centerImg(self.image, self.cfg.FRAME.IMG_SIZE)
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
            image = Image.new('RGBA', self.cfg.FRAME.IMG_SIZE , self.brightnessMask)
            self.image = imgutils.pasteImage(bgImage=self.image, fgImage=image)
        self.pm.hook.brightnessChangeAfter(app=self, brightness=brightness)

    def show(self):
            self.pm.hook.imageChangeBefore(app=self)
            self.setBrightness(self.brightness)
            if self.sendToFrame():
                self.pm.hook.imageChangeAfter(app=self)
                return True
    
    
    def setLoader(self):
        imgLoaders : list = self.pm.hook.imageLoader(app=self)
        if imgLoaders:
            self.imgLoader = imgLoaders[0]
        else:
            LOGGER.error(f"Missing Image Loader plugin. Imstall it with: pip install samsungframe/plugins/loadimgurl")
        return self.imgLoader


    def load(self, buffer : bytes = None) -> bool:
        """loads a new image. Buffer is here to force a specific image from plugins"""
        self.remotelyUploaded = False #turn the flag off
        self.idleIter = 0
        if not buffer:
            buffer = self.imgLoader.load()
        self.loadedImage = imgutils.bytes2img(buffer)
        self.loadedImage = imgutils.exifTranspose(self.loadedImage)
        self.forceLoad = False #new image has been loaded or it failed
        return True #must returns True if success because of plugins

    def resize(self):
        """Resize to fit the frame"""
        ret = self.pm.hook.ResizeBefore(app=self)
        if ret and any(ret): #at least one ResizeBefore returned True
            self.resizedImage = self.image
        else:
            self.resizedImage = imgutils.resize_and_centerImg(self.image, self.cfg.FRAME.IMG_SIZE)
        self.image = self.resizedImage
        self.pm.hook.ResizeAfter(app=self)

    def setStage(self, stage : int ):
        """For calling from plugins. Sets correct image for the stage"""
        if stage == self.Stage.RESIZE:
            self.image = self.loadedImage
        if stage == self.Stage.SHOW:
            self.image = self.resizedImage
        self.stage = self.Stage(stage)
        with self.cond: 
            self.cond.notify_all() #inform idle sleep if the stage change request was started from a different thread

        LOGGER.debug(f"New stage SET {self.stage.name}")

    def stages(self):
        """stage manager. Route is: load -> resize -> show -> idle"""
        while not self.quit:
            if self.stage == self.Stage.LOAD:
                self.load()
            elif self.stage == self.Stage.RESIZE:
                self.resize()
            elif self.stage == self.Stage.SHOW:
                if not self.show(): 
                    time.sleep(10) #connection lost. Request was too fast etc.
            elif self.stage == self.Stage.IDLE:
                self.idle()
            self.setStage(self.stage.nextStage())

    def saveCfg(self, path):
        data = self.cfg.as_dict()
        dbox = DynaBox(data).to_dict()
        loaders.write(filename=osp.join(path,"settings.toml"), data=dbox, merge=True)

    @staticmethod
    def loadCfg(section : str, data : dict):
        global settings
        setattr(settings,section, settings.get(section,data))

    def run(self):
        self.cfg = settings
        self.get_plugin_manager()

        self.pm.hook.loadCfg(app=self) #loads defaults

        pl = self.pm.list_name_plugin()
        print(pl)
        for p in pl:
            pname = p[0]
            if hasattr( self.cfg , pname):
                print(self.cfg[pname])

        self.pm.hook.startup(app=self)
        self.delay = self.cfg.FRAME.DELAY
        if not self.setLoader(): return
        try:
            self.stages()
        except KeyboardInterrupt:
            LOGGER.info("Interrupted")
        self.pm.hook.exit(app=self)
        
slideShow : SlideShow = None
if __name__ == '__main__':
    realPath = osp.join(osp.realpath(osp.dirname(__file__)))
    settings = Dynaconf(
        envvar_prefix="FRAME",
        settings_files=[osp.join(realPath,'settings.toml'), osp.join(realPath,'.secrets.toml')]
        )

    LOGGER.basicConfig(level=settings.FRAME.LOGLEVEL, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
    slideShow = SlideShow()
    slideShow.run()
