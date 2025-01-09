import plugins
PLUGIN_NAME = "<PLUGINNAME>" # set plugin name here. This must be the same as prefix of this file.
PLUGIN_FANCY_NAME = "<PLUGIN_FANCY_NAME>" # set fancy name for remote controller here
PLUGIN_CLASS = "<CLASS>" # Classes are: LOADER (force load after change), DISPLAY (at least one must stay active), REMOTE(can't be unloaded from web)
PLUGIN_SORT_ORDER = <SORT_ORDER> #Order for remote controller dialogs. Ascending.
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

@plugins.hookimpl
def setAPI(app):
    """
    Placeholder for setting plugin specific REST API calls.
    Should contain:
    router = APIRouter()
    @router.get("/api_point")
        def api_point():
            return {"message": "Not implemented yet"}
    app.api.registerRouter(PLUGIN_NAME, router)
    """