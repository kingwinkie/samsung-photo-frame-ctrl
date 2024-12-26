import plugins
from imgurlloader import ImgLoaderURL
from remi import gui

PLUGIN_NAME="LOADIMGURL"
PLUGIN_FANCY_NAME = "URL downloader"
PLUGIN_CLASS = "LOADER"
PLUGIN_SORT_ORDER = 230
class MyImgURLLoader(ImgLoaderURL):
    def setRemote(self):
        lbl_url = gui.Label(f"URL:",style={'text-align':'Left'})
        tx_url = gui.TextInput(width=200, height=200, margin='10px')
        tx_url.set_value(self.url)
        tx_url.onchange.do(self.on_url_changed)
        return [lbl_url, tx_url]
    
    def on_url_changed(self, widget, value):
        self.url = value
        self.imageb = None # reset the downloaded image
        self.app.setStage(None) #force reload

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    app.imgLoaderURL = MyImgURLLoader()
    app.imgLoaderURL.url = app.cfg[PLUGIN_NAME].IMG_SOURCE_PATH
    app.imgLoaderURL.downloadLimit = app.cfg[PLUGIN_NAME].HTTP_DOWNLOAD_LIMIT
    app.imgLoaderURL.app = app

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config):
    """
    defaultConfig = {
        "IMG_SOURCE_PATH" : "https://random.imagecdn.app/1024/600",
        # "IMG_SOURCE_PATH" : "http://localhost:8082" # for IMG_SOURCE = URL
        "HTTP_DOWNLOAD_LIMIT" : 10,
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)

@plugins.hookimpl
def do(app):
    if hasattr(app, "imgLoaderURL"):
        app.imgLoaderURL.do()
    
@plugins.hookimpl
def setRemote(app):
    return app.imgLoaderURL.setRemote()
    
@plugins.hookimpl
def load(app) -> bytes:
    """Get image data. For loaders."""
    return app.imgLoaderURL.load()