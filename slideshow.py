#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as LOGGER
import resize
import time
import plugins
from os import path as osp
from PIL import Image
from dynaconf import Dynaconf,loaders
from dynaconf.utils.boxing import DynaBox
import plugins.hookspecs as hookspecs

class SlideShow:
    image : Image = None
    pm : plugins.FramePluginManager = None
    cfg : Dynaconf = None
    quit : bool = False #quit requested from a plugin

    def quitApp(self, quit = True):
        self.quit = quit

    def delayPluginsDo(self, delay : float):
        """Calls do() in plugins"""
        wait = 1 # wait 1s
        for _ in range(0,delay,wait):
            start = time.time()
            self.pm.hook.do(app=self) #call plugins
            delta = time.time() - start #measure time lost in plugins
            waitD = wait - delta
            if waitD > 0 and not quit:
                time.sleep(waitD)
            
    def get_plugin_manager(self):
        self.pm = plugins.FramePluginManager("slideshow")
        self.pm.add_hookspecs(hookspecs)
        self.pm.load_all_plugins(self.cfg.FRAME.PLUGINS_ACTIVE)
        
    def sendToFrame(self):
        ret : list[bool] = self.pm.hook.showImage(app=self)
        if ret and len(ret)>0 and ret[0]: 
            return True

    def showImagePlugins(self, image : Image):
        if image:
            self.image = image
            self.pm.hook.imageChangeBefore(app=self)
            if self.pm.hook.showImage(app=self):
                self.pm.hook.imageChangeAfter(app=self)

    def show(self, imgLoader):
        buffer : bytes = imgLoader.load()
        if buffer:
            resizedImg = resize.resize_and_center(buffer, self.cfg.FRAME.IMG_SIZE)
            if resizedImg:
                self.image = resizedImg
                self.pm.hook.imageChangeBefore(app=self)
                if self.sendToFrame():
                    self.pm.hook.imageChangeAfter(app=self)
                    return True

    def slideShow(self, delay : float = None):
        if delay == None: delay=self.cfg.FRAME.DELAY
        imgLoaders : list = self.pm.hook.imageLoader(app=self)
        if imgLoaders:
            imgLoader = imgLoaders[0]
        else:
            LOGGER.error(f"Missing Image Loader plugin. Imstall it with: pip install samsungframe/plugins/loadimgurl")
            return
        while delay:
            if self.show(imgLoader): 
                self.delayPluginsDo(delay)
                if self.quit: return #quit was rerquested from a plugin
            else:
                time.sleep(15) #connection lost. Fast request


    def saveCfg(self, path):
        data = self.cfg.as_dict()
        dbox = DynaBox(data).to_dict()
        loaders.write(filename=osp.join(path,"settings.toml"), data=dbox, merge=True)

    @staticmethod
    def loadCfg(section : str, data : dict):
        global settings
        setattr(settings,section, settings.get(section,data))

    def run(self, realPath):
        self.cfg = settings
        self.get_plugin_manager()
        self.pm.hook.loadCfg(app=self) #loads defaults
        self.pm.hook.startup(app=self)
        try:
            self.slideShow()
        except KeyboardInterrupt:
            LOGGER.info("Interrupted")
        self.pm.hook.exit(app=self)
        
slideShow : SlideShow = None
if __name__ == '__main__':
    realPath = osp.join(osp.realpath(osp.dirname(__file__)))
    settings = Dynaconf(
        envvar_prefix="FRAME",
        settings_files=[  osp.join(realPath,'settings.toml'), osp.join(realPath,'.secrets.toml')],
       
        )

    LOGGER.basicConfig(level=settings.FRAME.LOGLEVEL, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
    slideShow = SlideShow()
    slideShow.run(realPath)
