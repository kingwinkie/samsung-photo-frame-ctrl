#!python3
# -*- coding: utf-8 -*-

import frame_ctrl
import sys
import logging as LOGGER
import config
import resize
import time
from enum import Enum
from loadimg import ImgLoaderURL, ImgLoaderFolder
LOGGER.basicConfig(level=config.LOGLEVEL)


class SOURCE(Enum):
    FOLDER = 1,
    URL = 2

def show(imgLoader):
    image = imgLoader.load()
    if image:
        resized = resize.resize_and_center(image)
        frame_ctrl.showImage(resized)

def main(source=config.IMG_SOURCE, path=config.IMG_SOURCE_PATH, ext=config.IMG_EXT, delay=config.DELAY):
    if source == SOURCE.FOLDER.value:
        imgLoader = ImgLoaderFolder(path, ext)
    elif source == SOURCE.URL.value:
        imgLoader = ImgLoaderURL(path)
    else:
        LOGGER.error(f"Incorrect Source ({source})")
        return
    while delay:
      show(imgLoader)
      time.sleep(delay)

main()
