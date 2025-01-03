import plugins
from imgaloader import ImgLoaderArtsy
from imgutils import drawText, HAlign, VAlign
import remi.gui as gui

PLUGIN_NAME = "LOADIMGARTSY"
PLUGIN_FANCY_NAME = "Artsy.net Gallery"
PLUGIN_CLASS = "LOADER"
PLUGIN_SORT_ORDER = 200

artsyImgLoader : ImgLoaderArtsy

@plugins.hookimpl
def imageChangeBefore(app):
    if app.loadedByPlugin == PLUGIN_NAME:
        app.image = drawText(text=artsyImgLoader.description, size=artsyImgLoader.size, fontSize=12, textColor=(192,192,192,192), align=(HAlign.RIGHT, VAlign.BOTTOM), bgImage=app.image, offset=(10,5))

@plugins.hookimpl
def startup(app):
    global artsyImgLoader
    artsyImgLoader = ImgLoaderArtsy(app.cfg[PLUGIN_NAME].CLIENT_ID,app.cfg[PLUGIN_NAME].CLIENT_SECRET,app.frameSize)
    artsyImgLoader.downloadLimit = app.cfg[PLUGIN_NAME].HTTP_DOWNLOAD_LIMIT
    artsyImgLoader.minAR = app.cfg[PLUGIN_NAME].MIN_ASPECT_RATIO
    artsyImgLoader.app = app

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
        "dynaconf_merge": True,
        "CLIENT_ID" : "client_id",
        "CLIENT_SECRET" : "client_secret",
        "HTTP_DOWNLOAD_LIMIT" : 10, # min delay between downloads in seconds
        "MIN_ASPECT_RATIO" : 1.2,
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)

@plugins.hookimpl
def do(app):
    artsyImgLoader.do()
        
@plugins.hookimpl
def load(app) -> bytes:
    """Get image data. For loaders."""
    return artsyImgLoader.load()

def on_change_ar(widget, value):
    artsyImgLoader.minAR = float(value)
    artsyImgLoader.app.setStage(None)

@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""
    contAR = gui.HBox()
    lblAR = gui.Label('Minimum required Aspect Ratio (W/H):', style={'text-align':'right'}, height=20, margin='4px')
    txtAR = gui.TextInput(single_line=True, width=60, height=20, margin='4px')
    txtAR.set_value(str(artsyImgLoader.minAR))
    txtAR.onchange.do( on_change_ar)
    contAR.append([lblAR,txtAR])
    return contAR
        

@plugins.hookimpl
def saveCfg(app) -> None:
    """called before startup
    Placeholder for plugin settings to be stored.
    Use app.saveCfg(PLUGIN_NAME, dict_with_config)
    """
    app.saveCfg(PLUGIN_NAME, { "dynaconf_merge": True,"MIN_ASPECT_RATIO": artsyImgLoader.minAR}, True)