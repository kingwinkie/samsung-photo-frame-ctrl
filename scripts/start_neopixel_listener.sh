#!/bin/sh

python=/home/pi/frame/.venv/bin/python
app_root=/home/pi/frame/samsungframe

sudo $python $app_root/plugins/ledstrip/listen.py &