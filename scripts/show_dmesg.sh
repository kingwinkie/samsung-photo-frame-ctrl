#!/bin/sh

python=/home/pi/frame/.venv/bin/python
app_root=/home/pi/frame/samsungframe
listing=$(dmesg  | tail -n 40)
$python $app_root/getips.py -th "$listing" | $python $app_root/txt2img.py -o - -fs 10 -bi $app_root/res/wifibg.jpg | sudo $python $app_root/show-image.py