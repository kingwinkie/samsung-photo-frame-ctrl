import plugins
from imgfolderloader import ImgLoaderFolder
from loadimg import ImgLoader


PLUGIN_NAME = "LOADIMGFOLDER"

@plugins.hookimpl
def imageChangeAfter(app):
    return None

@plugins.hookimpl
def startup(app):
    return None

@plugins.hookimpl
def exit(app):
    return None

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