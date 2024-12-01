
import neopixel
import ledconfig as config
import logging as LOGGER

closed = False
pixels = neopixel.NeoPixel(config.NEOPIXEL_GPIO, config.NEOPIXEL_LED, auto_write = False)

def limitChannel( color : int ) -> int:
    return color if color <= config.LED_BRIGHTNESS_LIMIT else config.LED_BRIGHTNESS_LIMIT

def limitRGB( color : tuple[int,int,int]) -> tuple[int,int,int]:
    return limitChannel(color[0]), limitChannel(color[1]), limitChannel(color[2])

def set(changes : tuple):
    if changes:    
        for change in changes:
            pixel = change[0]
            val = change[1]
            if pixel < config.NEOPIXEL_LED:
                pixels[pixel] = limitRGB(val)
        pixels.show()

def clean():
    LOGGER.debug("Neopixel clean()") 
    pixels.fill((0,0,0))
    pixels.show()

def fill(color : tuple):
    if color and not closed:
        LOGGER.debug(f"Neopixel fill({color})") 
        pixels.fill(limitRGB(color))
        pixels.show()

def close():
    global closed
    global pixels
    if not closed:
        if pixels:
            # pixels.deinit()
            closed = True
            del pixels
        