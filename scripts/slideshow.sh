#!/usr/bin/env bash
app_root=/home/pi/frame/samsungframe
venv=/home/pi/frame/.venv
sudo $venv/bin/python $app_root/slideshow.py >> /home/pi/frame/lo
g.txt 2>> /home/pi/frame/err.txt
