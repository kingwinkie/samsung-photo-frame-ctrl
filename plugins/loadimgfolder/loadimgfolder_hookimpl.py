import plugins
import slideshow
from imgfolderloader import ImgLoaderFolder
from loadimg import ImgLoader


PLUGIN_NAME = "LOADIMGFOLDER"
PLUGIN_FANCY_NAME = "Local Folder"
PLUGIN_CLASS = "LOADER"
PLUGIN_SORT_ORDER = 220
@plugins.hookimpl
def showImage(app : slideshow.SlideShow) -> bool:
     """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """
     
@plugins.hookimpl
def imageChangeAfter(app : slideshow.SlideShow) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc.
    """

@plugins.hookimpl
def startup(app : slideshow.SlideShow) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    app.imgLoaderFolder = ImgLoaderFolder(app.cfg[PLUGIN_NAME].IMG_SOURCE_PATH, imgExt=app.cfg[PLUGIN_NAME].IMG_EXT)

@plugins.hookimpl
def exit(app : slideshow.SlideShow) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """


@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config):
    """
    defaultConfig = {
        "IMG_SOURCE_PATH" : "data",
        "IMG_EXT" : "jpg", # folder filtering extension
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)


@plugins.hookimpl
def load(app) -> bytes:
    """Get image data. For loaders."""
    return app.imgLoaderFolder.load()