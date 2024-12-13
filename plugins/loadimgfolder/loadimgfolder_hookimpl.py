import plugins
import slideshow
from imgfolderloader import ImgLoaderFolder
from loadimg import ImgLoader


PLUGIN_NAME = "LOADIMGFOLDER"

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
    app.imgLoaderFolder = ImgLoaderFolder(loaderconfig.IMG_SOURCE_PATH, imgExt=loaderconfig.IMG_EXT)

@plugins.hookimpl
def exit(app : slideshow.SlideShow) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """

@plugins.hookimpl
def imageLoader(app) -> ImgLoader:
    imgLoader = ImgLoaderFolder(app.cfg.LOADIMGFOLDER.IMG_SOURCE_PATH, imgExt=app.cfg.LOADIMGFOLDER.IMG_EXT)
    return imgLoader


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
