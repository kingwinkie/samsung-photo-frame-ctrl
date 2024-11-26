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
from neopixelproc.sender import Sender, calcColor
from neopixelproc import config as ledConfig
from PIL import Image

ledSender : Sender = None
class SOURCE(Enum):
    FOLDER = 1,
    URL = 2

def ledstrip(img : Image):
    width = len(ledConfig.LED_TOP)
    height = len(ledConfig.LED_RIGHT)
    ledImage : Image.Image = img.resize((width, height))
    if ledImage:
        for x in range(width): 
            color : tuple = ledImage.getpixel((ledConfig.LED_TOP.start + x, 0))
            ledSender.addQueue((x,calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))
            color : tuple = ledImage.getpixel((x, height - 1))
            ledSender.addQueue((ledConfig.LED_BOTTOM.stop - x - 1, calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))
        for y in range(height):
            color : tuple = ledImage.getpixel((width - 1, y))
            ledSender.addQueue((ledConfig.LED_RIGHT.start + y, calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))
            color : tuple = ledImage.getpixel((0, y))
            ledSender.addQueue((ledConfig.LED_LEFT.stop - y - 1, calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))
                

def sendToFrame(img : Image):
    ret : bool = False
    buffer : bytes = resize.imgToBytes(img)
    if buffer:
        while not ret:
            ret = frame_ctrl.showImage(buffer)
            if not ret:
                time.sleep(5) #the frame is not in monitor mode, has been disconnected etc.
    return ret


def show(imgLoader):
    ret : bool = False
    buffer : bytes = imgLoader.load()
    if buffer:
        resizedImg = resize.resize_and_center(buffer)
        if resizedImg:
            ret = sendToFrame(resizedImg)
            if ret and config.LEDSTRIP_ENABLED:
                ledstrip(resizedImg)
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
    global ledSender
    with Sender(authkey=ledConfig.AUTHKEY,address=(ledConfig.ADDRESS,ledConfig.PORT)) as ledSender:
        if ledSender:
            time.sleep(0.5) #wait for sender thread init
        try:
            slideShow()
        except KeyboardInterrupt:
            LOGGER.info("Interrupted")
    return 0 # success

if __name__ == '__main__':
  LOGGER.basicConfig(level=config.LOGLEVEL, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
  sys.exit(main())
