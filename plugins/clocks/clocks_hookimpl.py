import plugins
import imgutils
from slideshow import SlideShow
from loadimg import ImgLoader

from PIL import Image
import time

PLUGIN_NAME = "CLOCKS"
class Clocks:
    currentImage : Image
    app : SlideShow
    shownTime : str = ""
    def getTime(self) -> str:
        text : str = time.strftime('%H:%M' if self.app.cfg.CLOCKS.FORMAT == "24h" else '%l:%M')
        return text
    def showTime(self):
        size = self.app.cfg.FRAME.IMG_SIZE
        text : str = self.getTime()
        self.app.image = imgutils.drawText(text=text, size=size, fontSize=200, textColor=(255,255,255,255), align=(imgutils.HAlign.CENTER, imgutils.VAlign.CENTER), bgImage=self.currentImage)
        self.shownTime = text



@plugins.hookimpl
def imageChangeAfter(app):
    return None

@plugins.hookimpl
def startup(app):
    clocks = Clocks()
    clocks.app = app
    app.clocksPlugin = clocks

@plugins.hookimpl
def exit(app):
    return None

@plugins.hookimpl
def imageChangeBefore(app : SlideShow) -> None:
    app.clocksPlugin.currentImage=app.image
    app.clocksPlugin.showTime()

@plugins.hookimpl
def do(app : SlideShow) -> None:
    clocks : Clocks = app.clocksPlugin
    now = clocks.getTime()
    if now != clocks.shownTime:
        clocks.showTime()
        app.sendToFrame()

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config):
    """
    defaultConfig = {
        "FORMAT" : "24h",
        "FILL" : "white"
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)