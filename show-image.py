#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import frame_ctrl
import sys
import logging as LOGGER
import config
import resize
LOGGER.basicConfig(level=config.LOGLEVEL)

def main():
  inBuffer = None
  if len(sys.argv) < 2 or sys.argv[1] == "-":
    inBuffer = sys.stdin
  else:
    inBuffer = open(sys.argv[1],"rb")

  resized = resize.resize_and_center(inBuffer)
  return frame_ctrl.showImage(resized)

sys.exit(main())
