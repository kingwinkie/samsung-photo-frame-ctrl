#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import sys
import time
import logging as LOGGER
import config
import usb.core
from usb.util import *
# the image must be in 1024x600 JPEG format

vendorId = 0x04e8 #Samsung

#List of codes taken from here: https://github.com/MOA-2011/3rdparty-plugins/blob/f11349bc643ac9664276734897c6ab9a4e1d58ba/LCD4linux/src/Photoframe.py
models = {
  'SPF72H':(0x200a, 0x200b),
  'SPF75H/76H':(0x200e, 0x200f),
  'SPF83H':(0x200c, 0x200d),
  'SPF85H/86H':(0x2012, 0x2013),
  'SPF85P/86P':(0x2016, 0x2017),
  'SPF87Hold':(0x2025, 0x2026), #old firmware
  'SPF105P':(0x201c, 0x201b),
  'SPF107H':(0x2035, 0x2036),
  'SPF107Hold':(0x2027, 0x2028) #old firmware
  'SPF700T':(0x204f, 0x2050),
  }

chunkSize = 0x4000
bufferSize = 0x20000

def expect(result, verifyList):
  resultList = result.tolist()
  if resultList != verifyList:
    LOGGER.error(f"Warning: Expected  {verifyList}  but got {resultList}", file=sys.stderr)

def storageToDisplay(dev):
  LOGGER.debug("Setting device to display mode")
  try:
    dev.ctrl_transfer(CTRL_TYPE_STANDARD | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0xfe, 0xfe, 254)
  except usb.core.USBError as e:
    errorStr = str(e)
    if errorStr != 'No such device (it may have been disconnected)' and e.errno != 5:
      raise e

def displayModeSetup(dev):
  LOGGER.debug("Sending setup commands to device")
  result = dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x04, 0x00, 0x00, 1)
  expect(result, [ 0x03 ])

def paddedBytes(buf, size):
  diff = size - len(buf)
  return buf + bytes(b'\x00') * diff

def chunkyWrite(dev, buf):
  for pos in range(0, bufferSize, chunkSize):
    dev.write(0x02, buf[pos:pos+chunkSize])

def writeImage(dev, content):
  size = struct.pack('I', len(content))
  header = b'\xa5\x5a\x09\x04' + size + b'\x46\x00\x00\x00'
  content = header + content

  for pos in range(0, len(content), bufferSize):
    buf = paddedBytes(content[pos:pos+bufferSize], bufferSize)
    chunkyWrite(dev, buf)
  
def show(content, model):
  v=models[model]
  dev = usb.core.find(idVendor=vendorId, idProduct=v[0])
  if dev:
    LOGGER.debug(f"Found {model} in storage mode")
    storageToDisplay(dev)
    time.sleep(2)
    dev = None
  if not dev:
    dev = usb.core.find(idVendor=vendorId, idProduct=v[1])

  if dev:
    LOGGER.debug(f"Found {model} in display mode")
    if not dev.get_active_configuration():
      dev.set_configuration()
    displayModeSetup(dev)
    writeImage(dev, content)
    usb.util.dispose_resources(dev)
    return 1      
  return -1

def showImage(content):
  ret = -1
  if content:
    if hasattr(config,'MODEL') and config.MODEL:
      ret = show(content, config.MODEL)
    else:
      for model in models:
        ret = show(content, model)
  if ret < 0:
    LOGGER.error("No supported devices found")
  return ret

