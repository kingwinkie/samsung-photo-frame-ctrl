import plugins
from loadimg import ImgLoader
from imgaloader import ImgLoaderArtsy
from imgutils import bytes2img, imgToBytes
from imgutils import drawText, HAlign, VAlign

PLUGIN_NAME = "LOADIMGARTSY"

@plugins.hookimpl
def imageChangeBefore(app):
    artsyImgLoader : ImgLoaderArtsy = app.artsyImgLoader
    text=f"{artsyImgLoader.artwork['slug']} ({artsyImgLoader.artwork['date']})"
    app.image = drawText(text=text, size=artsyImgLoader.size, fontSize=12, textColor=(192,192,192,192), align=(HAlign.RIGHT, VAlign.BOTTOM), bgImage=app.image, offset=(10,5))
    return None

@plugins.hookimpl
def startup(app):
    return None

@plugins.hookimpl
def exit(app):
    return None

@plugins.hookimpl
def imageLoader(app) -> ImgLoader:
    artsyImgLoader = ImgLoaderArtsy(app.cfg[PLUGIN_NAME].CLIENT_ID,app.cfg[PLUGIN_NAME].CLIENT_SECRET,app.cfg.FRAME.IMG_SIZE)
    artsyImgLoader.downloadLimit = app.cfg[PLUGIN_NAME].HTTP_DOWNLOAD_LIMIT
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
        
