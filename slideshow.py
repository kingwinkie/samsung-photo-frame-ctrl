#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as LOGGER
import imgutils as imgutils
import time
import plugins
from os import path as osp
from PIL import Image, ImageDraw
from dynaconf import Dynaconf,loaders
from dynaconf.utils.boxing import DynaBox
import plugins.hookspecs as hookspecs

class SlideShow:
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

    @property
    def brightness(self):
        return 255-self.brightnessMask[3]
    def quitApp(self, quit = True):
        self.quit = quit

    def idle(self):
        """Calls do() in plugins"""
        wait = 1 # wait 1s
        self.idleIter : int = 0
        while self.idleIter < self.delay or self.paused:
            self.idleIter += wait
            start = time.time()
            self.pm.hook.do(app=self) #call plugins
            delta = time.time() - start #measure time lost in plugins
            waitD = wait - delta
            if self.quit: return
            if self.forceLoad: return
            if waitD > 0:
                time.sleep(waitD)
            
    def get_plugin_manager(self):
        self.pm = plugins.FramePluginManager("slideshow")
        self.pm.add_hookspecs(hookspecs)
        self.pm.load_all_plugins(self.cfg.PLUGINS.ACTIVE)
        
        
    def sendToFrame(self):
        """Shows the image at defined frames"""
        self.imageBeforeEffects = self.image
        self.pm.hook.imageChangeBeforeEffects(app=self) # call effect plugins here (for nightmode etc.)
        ret : list[bool] = self.pm.hook.showImage(app=self)
        if ret and len(ret)>0 and ret[0]: 
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
            # Initialize the drawing context
            ImageDraw.Draw(image)
            self.image = imgutils.pasteImage(bgImage=self.image, fgImage=image)
        self.pm.hook.brightnessChangeAfter(app=self, brightness=brightness)

    def show(self):
        if self.loadedImage:
            self.image = self.loadedImage
            self.pm.hook.imageChangeBefore(app=self)
            self.setBrightness(self.brightness)
            self.idleIter = 0
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


    def loadImg(self, buffer : bytes = None) -> bool:
        if not buffer:
            buffer = self.imgLoader.load()
        if buffer:
            self.loadedImage = imgutils.resize_and_center(buffer, self.cfg.FRAME.IMG_SIZE)
            self.forceLoad = False #new image has been loaded
            if self.loadedImage: return True
        return False

    def stages(self):
        """stage manager. Route is load -> show -> idle"""
        while not self.quit:
            # load stage
            self.loadImg()
            # show stage
            if self.show(): 
                #idle stage
                self.idle()
                if self.quit: return #quit was rerquested from a plugin
            else:
                time.sleep(10) #connection lost. Request was too fast etc.
                self.idle(self.delay)


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
