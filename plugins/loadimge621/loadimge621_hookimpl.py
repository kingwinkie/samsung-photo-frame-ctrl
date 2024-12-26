import plugins
from py621 import types as py621Types
from imgeloader import ImgLoaderE621
from remi import gui
PLUGIN_NAME = "LOADIMGE621"
PLUGIN_FANCY_NAME = "E621 Gallery"
PLUGIN_CLASS = "LOADER"
PLUGIN_SORT_ORDER = 210
class MyImgELoader(ImgLoaderE621):
    def setRemote(self):
        """For setting web based remote from plugins. Returns list of remi.Widgets"""
        apis = list(map(lambda x: str(x)[5:],py621Types.EAPI))
        lbl_api = gui.Label(f"API:",style={'text-align':'Left'})
        dd_api = gui.DropDown.new_from_list(apis,width=200, height=20, margin='4px')
        dd_api.set_value(self.app.cfg[PLUGIN_NAME].API)
        dd_api.onchange.do(self.on_dd_api_change)
        lbl_tags = gui.Label(f"tags:",style={'text-align':'Left'})
        lv_tags = gui.ListView.new_from_list(self.app.cfg[PLUGIN_NAME].TAGS, width=300, height=120, margin='4px')
        bt_add = gui.Button('Add', width=100, height=20,  margin='4px')
        bt_add.onclick.do(self.on_bt_add_pressed)
        return [lbl_api, dd_api, lbl_tags, lv_tags, bt_add]
    
    def on_bt_add_pressed(self, widget):
            ...

    def on_dd_api_change(self, widget, value):
        self.api = value
        self.url = None # force load new URL
        self.imageb = None # reset the downloaded image
        self.pages = self.app.cfg[PLUGIN_NAME].PAGES #has to be re-read from config
        self.app.setStage(None) #force reload
        
pluginImgLoaderE = MyImgELoader() 
@plugins.hookimpl
def imageChangeAfter(app):
    return None

@plugins.hookimpl
def startup(app):
    pluginImgLoaderE.app = app
    pluginImgLoaderE.pages = app.cfg[PLUGIN_NAME].PAGES
    pluginImgLoaderE.api = app.cfg[PLUGIN_NAME].API
    pluginImgLoaderE.tags = app.cfg[PLUGIN_NAME].TAGS
    pluginImgLoaderE.downloadLimit = app.cfg[PLUGIN_NAME].HTTP_DOWNLOAD_LIMIT
    pluginImgLoaderE.url = pluginImgLoaderE.getURL() #download first URL
    return None

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
        "API" : "e621",
        "TAGS" : ["status:active", "ratio:>1.2" ,"-my_little_pony"], # your tags
        "HTTP_DOWNLOAD_LIMIT" : 10, # min delay between downloads in seconds
        "PAGES" : 700 # insert max history in pages you're interested in
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)

@plugins.hookimpl
def do(app):
    pluginImgLoaderE.do()
    
        
@plugins.hookimpl
def setRemote(app):
    return pluginImgLoaderE.setRemote()
    
@plugins.hookimpl
def load(app) -> bytes:
    """Get image data. For loaders."""
    return pluginImgLoaderE.load()