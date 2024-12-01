#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as LOGGER
import ledconfig as config
if config.DUMMY:
    import pixel_dummy as pixel
else:
    import pixel
from multiprocessing.connection import Listener
import time
import signal
import sys

LOGGER.basicConfig(level=config.LOGLEVEL)

exiting = False

def exit_gracefully(signum, frame):
    global exiting
    if exiting: return None
    exiting = True
    LOGGER.info(f"Neopixel Terminating") 
    pixel.clean()
    pixel.close()
    sys.exit()
    
    

def listen(listener : Listener) -> None:
    try:
        with listener.accept() as conn:
            LOGGER.info(f"connection accepted from {listener.last_accepted}") 
            pixel.clean()
            while conn and not exiting:
                try:
                    datab = conn.recv_bytes()
                    LOGGER.debug(f"Data recieved {datab}") 
                    length = len(datab)
                    data = []
                    for n in range(0,length,4):
                        if exiting: return None
                        pixelB = (datab[n:n+4])
                        if len(pixelB) == 4:
                            data.append((pixelB[0],tuple(pixelB[1:])))
                    pixel.set(data)
                except (EOFError, ConnectionResetError) as e:
                    LOGGER.error(f"Connection closed {e}") 
                    conn = None
                    pass #ignore
    except( OSError ) as e:
        if str(e)=='bad message length': # Bad message length, ignore. Has no errorno!
            LOGGER.error(str(e)) 
            pass

def main():
    signal.signal(signal.SIGINT, exit_gracefully)
    #signal.signal(signal.SIGTERM, exit_gracefully)
    pixel.clean()
    LOGGER.info(f"Neopixel Listener starting") 
    pixel.fill((config.LED_BRIGHTNESS_LIMIT,0,0)) # check red
    time.sleep(0.3)
    pixel.fill((0,config.LED_BRIGHTNESS_LIMIT,0)) # check green
    time.sleep(0.3)
    pixel.fill((0,0,config.LED_BRIGHTNESS_LIMIT)) # check blue
    time.sleep(0.3)
    pixel.clean()
    address = (config.ADDRESS, config.PORT)
    LOGGER.info(f"Address: {address}") 
    with Listener(address = address, authkey = config.AUTHKEY, family="AF_INET" ) as listener:
        try:
            while not exiting:
                LOGGER.info(f"Neopixel Listener is waiting for connection at {listener.address}") 
                pixel.clean() # set soft white as waiting for initial connection indicator
                listen(listener)
        except KeyboardInterrupt:
            pass


    pixel.clean()
    
    LOGGER.info(f"Closed") 

main()
