import plugins
from loadimg import ImgLoader
from imgaloader import ImgLoaderArtsy
PLUGIN_NAME = "LOADIMGARTSY"

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
    artsyImgLoader = ImgLoaderArtsy(app.cfg.LOADIMGARTSY.CLIENT_ID,app.cfg.LOADIMGARTSY.CLIENT_SECRET)
    artsyImgLoader.downloadLimit = app.cfg.LOADIMGARTSY.HTTP_DOWNLOAD_LIMIT
    app.artsyImgLoader = artsyImgLoader
    return artsyImgLoader

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config):
    """
    defaultConfig = {
        "CLIENT_ID" : "client_id",
        "CLIENT_SECRET" : "client_secret",
        "HTTP_DOWNLOAD_LIMIT" : 10, # min delay between downloads in seconds
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)

@plugins.hookimpl
def do(app):
    artsyImgLoader : ImgLoaderArtsy = app.artsyImgLoader
    if artsyImgLoader.areWeSafe(): #time test from last download
        if not artsyImgLoader.isReady():
            artsyImgLoader.prepare()
        
