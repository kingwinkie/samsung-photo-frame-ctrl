Samsung photo frame control with download ability for Raspberry Zero
=================

Slightly modified version of [Gekkio/samsung-photo-frame-ctrl](https://github.com/Gekkio/samsung-photo-frame-ctrl)
Intended use is to use Raspberry Zero W in combination with Samsung photo frame to show photos downloaded from the internet.

Main differences are:
* Added support for second version (firmware 10.08) of SPF-107H.
* Implemented logging
* Added download through Curl
* Added reading from local folder
* Added PIL for resizing picture
* Added config.py for more settings

Features
--------

* If a photo frame is in mass storage mode, the program will change it into mini display mode.
* If a photo frame is in mini display mode, the program will send the jpeg that was specified as the program argument to the photo frame. *The JPEG must be prescaled to the exactly correct size!*
* window-in-frame.sh which shows a user selected application window in the photo frame (needs Imagemagick!)

Supported photo frames
----------------------

* SPF-107H,SPF-107H2
* SPF-87H

Dependencies
------------

* pyusb
* pillow
* pycurl
* certifi

Usage
-----

`sudo python3 ./slideshow.py`

