import plugins
from slideshow import SlideShow
from loadimg import ImgLoader
from PIL import Image, ImageDraw, ImageFont
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
        image = Image.new('RGBA', size , (0,0,0,0))
        # Initialize the drawing context
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(200)
        
        text : str = self.getTime()
        self.shownTime = text
        bbox = draw.textbbox((0, 0), text, font=font)
        textSize : tuple[int, int] = bbox[2] - bbox[0], bbox[3] - bbox[1]
        textPos : tuple[int, int] = (size[0] - textSize[0]) / 2, (size[1] - textSize[1]) / 2
        # Add text to image
        draw.text(textPos, text, self.app.cfg.CLOCKS.FILL, font=font)
        if self.currentImage:
            img : Image = self.currentImage.convert("RGBA")
            img.paste(image, mask=image)
            self.app.image = img.convert("RGB")



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
        app.sendToFrame(app.image)

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