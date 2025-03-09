Samsung photo frame control with download ability for Raspberry Zero
=================

A Solution for Samsung photo frame based on [Gekkio/samsung-photo-frame-ctrl](https://github.com/Gekkio/samsung-photo-frame-ctrl)
The intended use is to use Raspberry Pi Zero W in combination with Samsung photo frame to show photos downloaded from the Internet.

The main differences are:
* Added support for second version (firmware 10.08) of SPF-107H.
* Implemented logging
* Added downloading with Curl (Pycurl)
* Added reading from a local folder
* Added PIL for manipulating with pictures
* Added config.py for additional settings
* Added simple gallery with download or local folder option
* Added support for Neopixel Led strip as background ambient light
* Implemented CLI
* Added pluggy plugin system and developed few additional plugins

Features
--------
  
* frame_ctrl.py
  * If the photo frame is in mass storage mode, the program will change it into mini display mode.
  * If the photo frame is in mini display mode, the program will send the jpeg that was specified as the program argument to the photo frame. *The JPEG must be prescaled to the exactly correct size!*
    
* show-image.py
  * Resize and center the image specified as the program argument and call frame_ctrl to show the image
  * Can show text over the image
 
* slideshow.py
  * Fully pluggable slideshow for all supported frames
  * Dummy frame plugin for development
  * Plugin for background LED strip (Neopixel)
  * Plugin for Clocks (shows big clocks at the frame screen)
  * Plugin for Night Mode (Leds are turned off, lower contrast and warmer colors during night)
  * Plugins for image sources:
    * From a local folder
    * From a generic URL
    * From Artsy.net (requires user account and credentials)
    * From Google Photo (currently requires Google Cloud Account)

* txt2img.py 
  * Converts text to image. Output can be piped to show-image.py


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


Installation
------------
* clone the repository
* cd samsung-photo-frame-ctrl
* create venv (python -m venv .venv)
* create, check, add or modify settings.toml and .secrets.toml (there is a image setting in settings.toml that might have to be changed)
* .venv/bin/pip install -r requirements.txt
* sudo .venv/bin/python3 ./slideshow.py 

Usage
-----

`sudo /"pathto"/.venv/bin/python3 ./slideshow.py`

Show IP address(es) with background image:
`sudo /"pathto"/.venv/bin/python3 getips.py | python txt2img.py -bi res/wifibg.jpg -o - | python show-image.py`

On Raspberry Pi Zero W
-----
* Install the latest 64bit Raspbian Lite, boot your RPi:
* `mkdir /home/pi/frame`
* `sudo apt install python3 pip git`
* `python3 -m venv /home/pi/frame/.venv`
* `git clone https://github.com/bero158/samsung-photo-frame-ctrl /home/pi/frame/samsung-photo-frame-ctrl`
* try `/home/pi/frame/.venv/bin/python3 /home/pi/frame/samsung-photo-frame-ctrl/slideshow.py`
* add `/home/pi/frame/.venv/bin/python3 /home/pi/frame/samsung-photo-frame-ctrl/slideshow.py &` to /etc/rc.local before 'exit 0' row

In default settings there's a remote controller available through web at port 8088
