import plugins
import time
from slideshow import SlideShow
from sender import Sender, calcColor
import ledconfig as ledConfig
from PIL import Image

class LedStripPlugin:
    sender : Sender = None

    def startup(self):
        self.sender = Sender(authkey=ledConfig.AUTHKEY,address=(ledConfig.ADDRESS,ledConfig.PORT))
        self.sender.start()
        time.sleep(0.5) #wait for sender thread init

    def ledstrip(self, img : Image):
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

    def exit(self):
        self.sender.stop()

@plugins.hookimpl
def imageChangeAfter(app : SlideShow):
    app.ledStrip.ledstrip(app.lastShownImage)


@plugins.hookimpl
def startup(app : SlideShow):
    app.ledStrip = LedStripPlugin()
    app.ledStrip.startup()

@plugins.hookimpl
def exit(app : SlideShow):
    app.ledStrip.exit()
