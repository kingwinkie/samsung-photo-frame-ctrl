#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import frame_ctrl
import logging as LOGGER
import config
import resize
import time
from PIL import Image

import lib
import pluggy
import hookspecs

def get_plugin_manager():
    
    pm = pluggy.PluginManager("slideshow")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("slideshow")
    pm.register(lib)
    return pm

class SlideShow:
    lastShownImage : Image = None
    pm : pluggy.PluginManager = None

    def sendToFrame(self, img : Image):
        ret : bool = False
        buffer : bytes = resize.imgToBytes(img)
        if buffer:
            while not ret:
                ret = frame_ctrl.showImage(buffer)
                if not ret:
                    time.sleep(5) #the frame is not in monitor mode, has been disconnected etc.
        return ret


    def show(self, imgLoader):
        ret : bool = False
        buffer : bytes = imgLoader.load()
        if buffer:
            resizedImg = resize.resize_and_center(buffer)
            if resizedImg:
                if self.sendToFrame(resizedImg):
                    self.lastShownImage = resizedImg
                    self.pm.hook.imageChangeAfter(app=self)
        return ret

    def slideShow(self, delay=config.DELAY):
        imgLoaders : list = self.pm.hook.imageLoader(app=self)
        if imgLoaders:
            imgLoader = imgLoaders[0]
        else:
            LOGGER.error(f"Missing Image Loader plugin. Imstall it with: pip install samsungframe/plugins/loadimgurl")
            return
        while delay:
            if self.show(imgLoader): 
                time.sleep(delay)
            else:
                time.sleep(15) #connection lost. Fast request


    def run(self):
        self.pm = get_plugin_manager()
        self.pm.hook.startup(app=self)
        
        try:
            self.slideShow()
        except KeyboardInterrupt:
            LOGGER.info("Interrupted")
        self.pm.hook.exit(app=self)
        return 0 # success

if __name__ == '__main__':
  LOGGER.basicConfig(level=config.LOGLEVEL, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
  slideShow = SlideShow()
  slideShow.run()
