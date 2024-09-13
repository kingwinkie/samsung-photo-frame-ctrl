#!/home/tom/data/git/samsung-frame/.venv python3

import os
import struct
import sys
import time
import usb.core
from usb.util import *
# the image must be in 1024x600 JPEG format
# convert data/in.jpg -resize 2048x1200! data/imgsf.jpg

vendorId = 0x04e8
models = {'SPF-87H': (0x2033, 0x2034), 'SPF-107H1': (0x2027, 0x2028), 'SPF-107H2': (0x2035, 0x2036) }

chunkSize = 0x4000
bufferSize = 0x20000

def expect(result, verifyList):
  resultList = result.tolist()
  if resultList != verifyList:
    print(f"Warning: Expected  {verifyList}  but got {resultList}", file=sys.stderr)

def storageToDisplay(dev):
  print ("Setting device to display mode")
  try:
    dev.ctrl_transfer(CTRL_TYPE_STANDARD | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0xfe, 0xfe, 254)
  except usb.core.USBError as e:
    errorStr = str(e)
    if errorStr != 'No such device (it may have been disconnected)':
      raise e

def displayModeSetup(dev):
  print ("Sending setup commands to device")
  result = dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x04, 0x00, 0x00, 1)
  expect(result, [ 0x03 ])
#  result = dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x01, 0x00, 0x00, 2)
#  expect(result, [ 0x09, 0x04 ])
#  result = dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x02, 0x00, 0x00, 1)
#  expect(result, [ 0x46 ])

def paddedBytes(buf, size):
  diff = size - len(buf)
  return buf + bytes(b'\x00') * diff

def chunkyWrite(dev, buf):
  pos = 0
  while pos < bufferSize:
    dev.write(0x02, buf[pos:pos+chunkSize])
    pos += chunkSize

def writeImage(dev):
#  result = dev.ctrl_transfer(CTRL_TYPE_STANDARD | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0x0300, 0x00, 255)
#  expect(result, [ 0x04, 0x03, 0x09, 0x04 ])

#  result = dev.ctrl_transfer(CTRL_TYPE_STANDARD | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0x0301, 0x0409, 255)

  if len(sys.argv) < 2 or sys.argv[1] == "-":
    content = sys.stdin.read()
  else:
    f = open(sys.argv[1],"rb")
    content = f.read()
    f.close()

  size = struct.pack('I', len(content))
  header = b'\xa5\x5a\x09\x04' + size + b'\x46\x00\x00\x00'

  content = header + content

  pos = 0
  while pos < len(content):
    buf = paddedBytes(content[pos:pos+bufferSize], bufferSize)
    chunkyWrite(dev, buf)
    pos += bufferSize

  
#  result = dev.ctrl_transfer(CTRL_TYPE_VENDOR | CTRL_IN | CTRL_RECIPIENT_DEVICE, 0x06, 0x00, 0x00, 2)
#  expect(result, [ 0x00, 0x00 ])

found = False

for k, v in models.items():
  dev = usb.core.find(idVendor=vendorId, idProduct=v[0])
  if dev:
    print (f"Found {k} in storage mode")
    storageToDisplay(dev)
    time.sleep(1)
    dev = usb.core.find(idVendor=vendorId, idProduct=v[1])
    found = True
  if not dev:
    dev = usb.core.find(idVendor=vendorId, idProduct=v[1])
  if dev:
    print (f"Found {k} in display mode")
    dev.set_configuration()
    displayModeSetup(dev)
    writeImage(dev)
    found = True

if not found:
  print ("No supported devices found", file=sys.stderr)
  sys.exit(-1)
