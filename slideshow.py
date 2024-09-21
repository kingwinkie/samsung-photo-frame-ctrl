#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import frame_ctrl
import sys
import logging as LOGGER
import config
import resize
import time
from enum import Enum
from loadimg import ImgLoaderURL, ImgLoaderFolder

class SOURCE(Enum):
    FOLDER = 1,
    URL = 2

def show(imgLoader):
    ret = False
    image = imgLoader.load()
    if image:
        resized = resize.resize_and_center(image)
        while not ret:
            ret = frame_ctrl.showImage(resized)
            if not ret:
                time.sleep(5) #the frame is not in monitor mode, has been disconnected etc.
    return ret


def slideShow(source=config.IMG_SOURCE, path=config.IMG_SOURCE_PATH, ext=config.IMG_EXT, delay=config.DELAY):
    if source == SOURCE.FOLDER.value:
        imgLoader = ImgLoaderFolder(path, ext)
    elif source == SOURCE.URL.value:
        imgLoader = ImgLoaderURL(path)
    else:
        LOGGER.error(f"Incorrect Source ({source})")
        return
    while delay:
      if show(imgLoader): 
        time.sleep(delay)
      else:
          time.sleep(15) #connection lost. Fast request


def main():
    try:
        slideShow()
    except KeyboardInterrupt:
        LOGGER.info("Interrupted")
    return 0 # success

if __name__ == '__main__':
  LOGGER.basicConfig(level=config.LOGLEVEL, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
  sys.exit(main())
