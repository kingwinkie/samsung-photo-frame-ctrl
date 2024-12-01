#!/bin/sh

python=/home/pi/frame/.venv/bin/python
app_root=/home/pi/frame/samsung-photo-frame-ctrl
text="WiFi is unavailable

Starting captive portal

Connect to AP PBFrame 

and set WiFi connection"
$python $app_root/txt2img.py -ti "$text" -o - -fs 20 -bi $app_root/res/wifibg.jpg -fp $app_root/font/Roboto-Bold.ttf | sudo $python $app_root/show-image.py