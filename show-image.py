#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import frame_ctrl
import sys
import logging as LOGGER
import resize
import argparse
import txt2img
import config
from PIL import Image
def main():
  parser = argparse.ArgumentParser(
                    prog='show-image',
                    description='This software renders image on Samsung Photo Frame connected to a USB port',
                    epilog="""
                    If there's no --input or specified the software reads from stdin.
                    """)
  parser.add_argument('-i','--input', help="Input image file")
  parser.add_argument('-t','--text', help="Reads text from stdin")
  parser.add_argument('-ti','--textinput', help="Input text file. '-' reads text from stdin")
  parser.add_argument('-v', '--verbose', action='store_true') 
    
  args = parser.parse_args()
  logLevel : LOGGER = LOGGER.DEBUG if args.verbose else LOGGER.ERROR
  LOGGER.basicConfig(level=logLevel)
  LOGGER.info("Starting")
  show : Image = None
  inBuffer = None
  if args.input:
     LOGGER.debug(f"Reading {args.input}")
     inBuffer = open(args.input,"rb")
     show = resize.resize_and_center(inBuffer)
  elif args.textinput:
     LOGGER.debug(f"Creating Image from text {args.textinput}")
     # create the image from the text
     txtImg : Image = txt2img.createImage(text=args.textinput,width=config.IMG_SIZE[0], height=config.IMG_SIZE[1])
     show = resize.resize_and_centerImg(txtImg)
  elif args.text:
     # create the image from text from stdin
     inputText = sys.stdin.read()
     LOGGER.debug(f"Creating Image from text {args.inputText}")
     txtImg : Image = txt2img.createImage(inputText,width=config.IMG_SIZE[0], height=config.IMG_SIZE[1])
     show = resize.resize_and_centerImg(txtImg)
  else:
    LOGGER.debug("Reading image from stdin")
    inBuffer = sys.stdin
    show = resize.resize_and_center(inBuffer)
  return frame_ctrl.showImage(show)

if (__name__ == "__main__"):
    main()