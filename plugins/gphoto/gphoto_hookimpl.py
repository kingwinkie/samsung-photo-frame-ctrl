import plugins
from imgutils import drawText, HAlign, VAlign
from gpapi import GPDownloader
PLUGIN_NAME = "GPHOTO" # set plugin name here. This must be the same as prefix of this file.
PLUGIN_FANCY_NAME = "Google Photo Gallery" # set fancy name for remote controller here
PLUGIN_CLASS = "LOADER" # Classes are: LOADER (force load after change), DISPLAY (at least one must stay active), REMOTE(can't be unloaded from web)
PLUGIN_SORT_ORDER = 210 #Order for remote controller dialogs. Ascending.
gpDownloader : GPDownloader= None
@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """

@plugins.hookimpl 
def load(app):
    """called when a new image is required
    Returns ImgLoader desc. object.
    """
    return gpDownloader.load()

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
    if app.loadedByPlugin == PLUGIN_NAME:
        app.image = drawText(text=gpDownloader.description, size=app.cfg.FRAME.IMG_SIZE, fontSize=12, textColor=(192,192,192,192), align=(HAlign.RIGHT, VAlign.BOTTOM), bgImage=app.image, offset=(10,5))


@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    global gpDownloader
    gpDownloader = GPDownloader()
    gpDownloader.counter = 0


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
    gpDownloader.do()
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

@plugins.hookimpl
def ResizeBefore(app):
    """Called before resize"""

@plugins.hookimpl
def ResizeAfter(app):
    """Called after resize"""

@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""

@plugins.hookimpl
def loadAfter(app):
    """Called after successful load"""