import ledconfig as config 
import logging as LOGGER
import time
from led_effects import PrivilegedSender
import led_effects as effects

LOGGER.basicConfig(level=config.LOGLEVEL)

def main():
    with PrivilegedSender(authkey=config.AUTHKEY,address=(config.ADDRESS,config.PORT),leds=config.LED_ALL) as sender:
        
        time.sleep(0.5) #wait for sender thread init
        shine = effects.Effect(sender,config.LED_ALL)
        color = (255,0,0)
        shine.fill(color)
        input()
        color = (0,255,0)
        shine.fill(color)
        input()
        color = (0,0,255)
        shine.fill(color)
        input()
        color = (255,255,255)
        shine.fill(color)
        input()
        

if __name__ == "__main__":
    main()