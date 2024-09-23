Samsung photo frame control with download ability for Raspberry Zero
=================

Slightly modified version of [Gekkio/samsung-photo-frame-ctrl](https://github.com/Gekkio/samsung-photo-frame-ctrl)
The intended use is to use Raspberry Pi Zero W in combination with Samsung photo frame to show photos downloaded from the Internet.

The main differences are:
* Added support for second version (firmware 10.08) of SPF-107H.
* Implemented logging
* Added downloading with Curl (Pycurl)
* Added reading from a local folder
* Added PIL for manipulating with pictures
* Added config.py for additional settings

Features
--------
* The behavior can be configured via config.py
  
* frame_ctrl.py
  * If the photo frame is in mass storage mode, the program will change it into mini display mode.
  * If the photo frame is in mini display mode, the program will send the jpeg that was specified as the program argument to the photo frame. *The JPEG must be prescaled to the exactly correct size!*
    
* show-image.py
  * Resize and center the image specified as the program argument and call frame_ctrl to show the image
 
* slideshow.py
  * In mode IMG_SOURCE = 1 (FOLDER) shows images from folder defined in IMG_SOURCE_PATH in random order
  * In mode IMG_SOURCE = 2 (URL) downloads images from URL defined in IMG_SOURCE_PATH


Supported photo frames
----------------------

* SPF72H
* SPF75H/76H
* SPF83H
* SPF85H/86H
* SPF85P/86P
* SPF87H old
* SPF105P
* SPF107H
* SPF107H old
* SPF700T

Dependencies
------------

* pyusb
* pillow
* pycurl
* certifi

Usage
-----

`sudo python3 ./slideshow.py`

On Raspberry Pi Zero W
-----
* Install the latest 64bit Raspbian Lite, boot your RPi:
* `mkdir /home/pi/frame`
* `sudo apt install python3 pip git`
* `python3 -m venv /home/pi/frame/.venv`
* `git clone https://github.com/bero158/samsung-photo-frame-ctrl /home/pi/frame/samsung-photo-frame-ctrl`
* try `/home/pi/frame/.venv/bin/python3 /home/pi/frame/samsung-photo-frame-ctrl/slideshow.py`
* add `/home/pi/frame/.venv/bin/python3 /home/pi/frame/samsung-photo-frame-ctrl/slideshow.py &` to /etc/rc.local before 'exit 0' row
