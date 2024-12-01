#!/bin/sh

python=/home/pi/frame/.venv/bin/python
app_root=/home/pi/frame/samsung-photo-frame-ctrl
ssid=$(iwgetid -r)
headertext="
Connected to:

$ssid

IP address:
"
$python $app_root/getips.py -th "$headertext" | $python $app_root/txt2img.py -o - -fs 20 -bi $app_root/res/wifibg.jpg -fp $app_root/font/Roboto-Bold.ttf | sudo $python $app_root/show-image.py