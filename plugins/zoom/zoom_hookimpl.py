import plugins
import imgutils
from PIL import Image
from imgutils import Dimension
import remi.gui as gui

PLUGIN_NAME = "ZOOM"

class Zoom():
    zoom : int # zoom in perc
    app = None
    def __init__(self, app):
        self.app = app
        self.zoom = 100

    def setRemote(self):
        self.lblZoom = gui.Label(f"Zoom: {self.zoom} %",style={'text-align':'Left'})
        
        self.remote_zoom = gui.Slider(self.zoom, 100, 500, 50, width=200, height=10, margin='1px')
        # setting the listener for the onclick event of the button
        self.remote_zoom.onchange.do(self.on_remote_zoom_changed)
        return [self.lblZoom, self.remote_zoom]

    def setZoomText(self):
        if hasattr(self, "lblZoom"):
            self.lblZoom.set_text(f"Zoom: {self.zoom}%")
        
    def on_remote_zoom_changed(self, widget, value):
        self.zoom = int(value)
        self.app.setStage(self.app.Stage.LOAD)
        self.setZoomText()
        
    def setZoom(self, zoom : int):
        self.zoom = zoom
        if hasattr(self, "lblZoom"):
            self.lblZoom.set_text(f"Zoom: {self.zoom}%")
        self.setZoomText()
        
@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """

@plugins.hookimpl 
def imageLoader(app):
    """called when a new image is required
    Returns ImgLoader desc. object.
    """

@plugins.hookimpl
def imageChangeAfter(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """

@plugins.hookimpl
def imageChangeBefore(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """
    

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    app.zoom = Zoom(app)

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """
    defaultConfig = {
        "VARIABLE1" : "default_value1",
        "VARIABLE2" : "default_value2",
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

@plugins.hookimpl
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """

@plugins.hookimpl
def showImage(app) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """

@plugins.hookimpl
def imageChangeBeforeEffects(app):
    """For post-effects aka NightMode. Called after imageChangeBefore and before showImage. Intended use is for global filters.
    """
    
@plugins.hookimpl
def brightnessChangeAfter(app, brightness : int) -> None:
    """called after brightness value was changed. Brightness is 0-255
    Intended as a feedback for remote
    """

def resize(img : Image, dimension : Dimension, imgSize : tuple[int, int], frameSize : tuple[int, int], zoom : int = 100):
    # image width < frame width
    diff = frameSize[dimension] - imgSize[dimension]
    diffP = diff * 100 / frameSize[dimension]

    if zoom != 100:
        newSize = imgSize[0] * zoom // 100, imgSize[1] * zoom // 100
        newPos = (newSize[0] - imgSize[0])//2, (newSize[1] - imgSize[1])//2
        img = img.resize(newSize)
        img = img.crop((*newPos,imgSize[0]+newPos[0],imgSize[1]+newPos[1]))
        return imgutils.resize_and_centerImg(img, frameSize, "black", imgutils.RMode.ZOOM)
    if diffP < 2:
        # we can freely resize the image. Distorsion < 2% is invisible
        return imgutils.pasteImageFrame(img, frameSize, (0,0), frameSize)
    elif diffP <= 15:
        # still add 2% and crop height
        imgSizeL = list(imgSize)
        imgSizeL[dimension] =  int(imgSizeL[dimension] * 1.02)
        imgSize = tuple(imgSizeL)
        #zoom
        size, pos = imgutils.resizeCenterCalc(imgSize,frameSize,imgutils.RMode.ZOOM)
        img = img.resize(size)
        return imgutils.pasteImageFrame(img, size, pos, frameSize)
    else:
        #difference is too big. Do nothing
        return imgutils.resize_and_centerImg(img, frameSize)
        
@plugins.hookimpl
def ResizeBefore(app):
    """Called before resize"""
    imgSize = app.image.size
    frameSize = app.cfg.FRAME.IMG_SIZE
    imgSizeNorm = imgutils.imgSizeCalc(imgSize, frameSize, imgutils.RMode.SHRINK)
    if imgSizeNorm[Dimension.WIDTH] < frameSize[Dimension.WIDTH]:
        # image width < frame width
        app.image = resize(app.image, Dimension.WIDTH, imgSizeNorm, frameSize, app.zoom.zoom)
    else:
        app.image = resize(app.image, Dimension.HEIGHT, imgSizeNorm, frameSize, app.zoom.zoom)
    return True


@plugins.hookimpl
def ResizeAfter(app):
    """Called after resize"""

@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""
    return 'Zoom', app.zoom.setRemote()
    

@plugins.hookimpl
def loadAfter(app):
    """Called after successful load"""
    app.zoom.setZoom(100) #set zoom back to 100%