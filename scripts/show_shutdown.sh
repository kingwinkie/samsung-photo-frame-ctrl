#!/bin/sh

python=/home/pi/frame/.venv/bin/python
app_root=/home/pi/frame/samsungframe
text="shutdown"
$python $app_root/txt2img.py -ti "$text" -o - -fs 50 -bi $app_root/res/textbg.jpg -fp $app_root/font/Amatic-Bold.ttf | sudo $python $app_root/showimage.py