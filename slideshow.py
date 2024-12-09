#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as LOGGER
import config
import resize
import time
from PIL import Image
import pluggy
import hookspecs
import threading
import remote.iface
import streamlit.web.bootstrap
import streamlit as st

def get_plugin_manager():
    
    pm = pluggy.PluginManager("slideshow")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("slideshow")
    return pm

class SlideShow:
    image : Image = None
    mainThread : threading.Thread = None
    size : tuple[int,int]
    pm : pluggy.PluginManager = None

    def blank(self) -> Image:
        image = Image.new('RGB',self.size,(0,0,0))
        return image

    def showImagePlugins(self, image : Image):
        if image:
            self.image = image
            self.pm.hook.imageChangeBegore(app=self)
            if self.pm.hook.showImage(app=self):
                self.pm.hook.imageChangeAfter(app=self)

    def show(self):
        ret : bool = False
        if False:
            image = self.blank()
        else:
            buffer = self.pm.hook.loadImage(app=self)[0]
            if buffer:
                image = resize.resize_and_center(buffer)
        self.showImagePlugins(image)
        return ret

    def slideShow(self, delay=config.DELAY):
        self.pm.hook.startup(app=self)
        time.sleep(10)
        
        try:
            while delay:
                #if remote.iface.quit: return
                if self.show(): 
                    time.sleep(delay)
                else:
                    time.sleep(15) #connection lost. Fast request
        except KeyboardInterrupt:
            LOGGER.info("Interrupted")
        self.pm.hook.exit(app=self)
        
    def main(self):
        
        self.pm = get_plugin_manager()
        self.size = config.IMG_SIZE

        
        self.mainThread = threading.Thread(target=self.slideShow,daemon=True)
        self.mainThread.start()
        remote.iface.interface.time = 10
        streamlit.web.bootstrap.run("remote/remote.py", False, [], []) # blocking
        
        return 0 # success

slideShow : SlideShow = None
if __name__ == '__main__':
  LOGGER.basicConfig(level=config.LOGLEVEL, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
  slideShow = SlideShow()
  slideShow.main()
