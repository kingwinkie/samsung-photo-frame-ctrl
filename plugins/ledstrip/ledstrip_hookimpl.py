import plugins
import time
from slideshow import SlideShow
from sender import Sender, calcColor
import ledconfig as ledConfig
from PIL import Image

PLUGIN_NAME = "LEDSTRIP"


class LedStripPlugin:
    sender : Sender = None
    turnedOn : bool = True
    def startup(self):
        self.sender = Sender(authkey=ledConfig.AUTHKEY,address=(ledConfig.ADDRESS,ledConfig.PORT))
        self.sender.start()
        self.turnedOn = True
        time.sleep(0.5) #wait for sender thread init

    def ledstrip(self, img : Image):
        if not img: return
        self.turnedOn = True
        width = len(ledConfig.LED_TOP)
        height = len(ledConfig.LED_RIGHT)
        ledImage : Image.Image = img.resize((width, height))
        if ledImage:
            for x in range(width): 
                color : tuple = ledImage.getpixel((ledConfig.LED_TOP.start + x, 0))
                self.sender.addQueue((x,calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))
                color : tuple = ledImage.getpixel((x, height - 1))
                self.sender.addQueue((ledConfig.LED_BOTTOM.stop - x - 1, calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))
            for y in range(height):
                color : tuple = ledImage.getpixel((width - 1, y))
                self.sender.addQueue((ledConfig.LED_RIGHT.start + y, calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))
                color : tuple = ledImage.getpixel((0, y))
                self.sender.addQueue((ledConfig.LED_LEFT.stop - y - 1, calcColor(color, ledConfig.LED_BRIGHTNESS_LIMIT)))

    def turnOff(self):
        if self.turnedOn:
            pixels = [(i,(0,0,0)) for i in ledConfig.LED_ALL]
            self.sender.addQueue(pixels)
            self.turnedOn = False

    def exit(self):
        self.sender.stop()

def isNightMode(app) -> bool:
    """Returns True if plugin Nightmode is in NIGHT mode. Otherwise returns False"""
    if hasattr(app, "nightmode"):
        mode : str = app.nightmode.getModeStr()
        if mode == "NIGHT" : return True
    return False



@plugins.hookimpl
def imageChangeAfter(app : SlideShow):
    if isNightMode(app):
        app.ledStrip.turnOff()
    else:
        app.ledStrip.ledstrip(app.image)

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config):
    """
    
  

@plugins.hookimpl
def startup(app : SlideShow):
    app.ledStrip = LedStripPlugin()
    app.ledStrip.startup()

@plugins.hookimpl
def exit(app : SlideShow):
    app.ledStrip.exit()

@plugins.hookimpl
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """
    if isNightMode(app):
        app.ledStrip.turnOff()
    else:
        if not app.ledStrip.turnedOn:
            app.ledStrip.ledstrip(app.image)