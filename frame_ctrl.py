#!python3
# -*- coding: utf-8 -*-

import struct
import sys
import time
import logging as LOGGER
import config
import usb.core
from usb.util import *
# the image must be in 1024x600 JPEG format

vendorId = 0x04e8
models = {'SPF-87H': (0x2033, 0x2034), 'SPF-107H1': (0x2027, 0x2028), 'SPF-107H2': (0x2035, 0x2036) }

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
  pos = 0
  while pos < bufferSize:
    dev.write(0x02, buf[pos:pos+chunkSize])
    pos += chunkSize

def writeImage(dev, content):
  size = struct.pack('I', len(content))
  header = b'\xa5\x5a\x09\x04' + size + b'\x46\x00\x00\x00'
  content = header + content

  pos = 0
  while pos < len(content):
    buf = paddedBytes(content[pos:pos+bufferSize], bufferSize)
    chunkyWrite(dev, buf)
    pos += bufferSize

  
def show(content, k, v):
  dev = usb.core.find(idVendor=vendorId, idProduct=v[0])
  if dev:
    LOGGER.debug(f"Found {k} in storage mode")
    storageToDisplay(dev)
    time.sleep(2)
    dev = None
  if not dev:
    dev = usb.core.find(idVendor=vendorId, idProduct=v[1])

  if dev:
    LOGGER.debug(f"Found {k} in display mode")
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
      ret = show(content, config.MODEL, models[config.MODEL])
    else:
      for k, v in models.items():
        ret = show(content, k, v)
  if ret < 0:
    LOGGER.error("No supported devices found")
  return ret

