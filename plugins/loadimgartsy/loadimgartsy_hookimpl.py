import plugins
from imgaloader import ImgLoaderArtsy
from imgutils import drawText, HAlign, VAlign

PLUGIN_NAME = "LOADIMGARTSY"
PLUGIN_FANCY_NAME = "Artsy.net Gallery"
PLUGIN_CLASS = "LOADER"
PLUGIN_SORT_ORDER = 200

@plugins.hookimpl
def imageChangeBefore(app):
    if app.loadedByPlugin == PLUGIN_NAME:
        artsyImgLoader : ImgLoaderArtsy = app.artsyImgLoader
        app.image = drawText(text=artsyImgLoader.description, size=artsyImgLoader.size, fontSize=12, textColor=(192,192,192,192), align=(HAlign.RIGHT, VAlign.BOTTOM), bgImage=app.image, offset=(10,5))

@plugins.hookimpl
def startup(app):
    artsyImgLoader = ImgLoaderArtsy(app.cfg[PLUGIN_NAME].CLIENT_ID,app.cfg[PLUGIN_NAME].CLIENT_SECRET,app.frameSize)
    artsyImgLoader.downloadLimit = app.cfg[PLUGIN_NAME].HTTP_DOWNLOAD_LIMIT
    app.artsyImgLoader = artsyImgLoader
    return artsyImgLoader

@plugins.hookimpl
def exit(app):
    return None


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
    app.artsyImgLoader.do()
    
        
@plugins.hookimpl
def load(app) -> bytes:
    """Get image data. For loaders."""
    return app.artsyImgLoader.load()