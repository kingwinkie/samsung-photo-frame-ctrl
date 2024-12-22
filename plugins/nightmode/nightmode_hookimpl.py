import plugins
import imgutils
from nightmode import Nightmode
from PIL import Image,  ImageDraw
PLUGIN_NAME = "NIGHTMODE"

def setMode(app):
    global lastImage
    mode = app.nightmode.getMode()
    app.nightmode.checkTTModeChange()
    app.nightmode.setMode(mode)
    app.nightmode.lastMode = mode


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
def imageChangeBeforeEffects(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """
    

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    app.nightmode = Nightmode()
    app.nightmode.createTT(app.cfg[PLUGIN_NAME].TIMES)
    app.nightmode.app = app
    app.nightmode.nightBrightness = app.cfg[PLUGIN_NAME].NIGHT_BRIGHTNESS

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """
    defaultConfig = {
        "NIGHT_BRIGHTNESS" : 10,
        "TIMES" : [("07:00", "day"),("22:00", "night")]
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

@plugins.hookimpl
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """
    if app.nightmode.lastMode != app.nightmode.getMode():
        setMode(app)

@plugins.hookimpl
def showImage(app) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """