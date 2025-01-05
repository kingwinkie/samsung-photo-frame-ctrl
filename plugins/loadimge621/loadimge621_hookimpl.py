import plugins
from py621 import types as py621Types
from imgeloader import ImgLoaderE621
from remi import gui
import logging as LOGGER

PLUGIN_NAME = "LOADIMGE621"
PLUGIN_FANCY_NAME = "E621 Gallery"
PLUGIN_CLASS = "LOADER"
PLUGIN_SORT_ORDER = 210
class MyImgELoader(ImgLoaderE621):
    ti_tags : list[gui.TextInput]
    tagRows : list[gui.Container] # list of tag text inputs
    tagsContainer : gui.Container
    api : py621Types.EAPI
    def setRemote(self):
        """For setting web based remote from plugins. Returns list of remi.Widgets"""
        apis = list(map(lambda x: str(x)[5:],py621Types.EAPI))
        lbl_api = gui.Label("API:",style={'text-align':'Left'})
        dd_api = gui.DropDown.new_from_list(apis,width=200, height=20, margin='4px')
        dd_api.set_value(self.api)
        dd_api.onchange.do(self.on_dd_api_change)
        
        lbl_tags = gui.Label("tags:",style={'text-align':'Left'})
        self.cont_tags = []
        self.tagRows = []
        for row, tag in enumerate(self.tags):
            tagRow = self.addTiTag(tag, row)
            self.tagRows.append(tagRow)
        self.tagsContainer = gui.Container(width=300, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center','margin': '4px'})            
        self.tagsContainer.append(self.tagRows)
        bt_tag_add = gui.Button('Add', width=100, height=20,  margin='4px')
        bt_tag_add.onclick.do(self.on_bt_add_pressed)
        return [lbl_api, dd_api, lbl_tags, self.tagsContainer, bt_tag_add]
    
    def addTiTag(self, tag : str, row : int) -> gui.Container:
        #ti_tag = gui.TextInput(width=200, height=20, margin='10px')
        #rowContainer = gui.Container(width=300, style={'display': 'inline', 'overflow': 'auto', 'margin': '0px'})            
        rowContainer = gui.Container(width=300, style={'display': 'inline'})            
        ti_tag = gui.TextInput(width=200, height=20, margin='4px', style={'float': 'left'})
        ti_tag.row = row
        ti_tag.set_value(tag)
        ti_tag.onchange.do(self.on_ti_tag_change)
        self.cont_tags.append(rowContainer)
        btX = gui.Button(text = "X", width=20, height=20, margin='4px', style={'float': 'left'})
        btX.row = row
        btX.onclick.do(self.on_btX_clicked)
        rowContainer.append([ti_tag, btX])
        rowContainer.ti_tag = ti_tag
        btX.rowContainer = rowContainer
        return rowContainer

    def reload(self):
        self.imageb = None
        self.app.setStage(None) #force reload

    def on_btX_clicked(self, widget):
        rowContainer : gui.Container = widget.rowContainer
        self.tagsContainer.remove_child(rowContainer)
        self.cont_tags.remove(rowContainer)
        self.rebuildTags()
        self.reload()

    def on_ti_tag_change(self, widget, value):
            self.rebuildTags()
            self.pages = self.app.cfg[PLUGIN_NAME].PAGES #has to be re-read from config
            self.reload()

    def rebuildTags(self):
        """re-creates internal array of tags"""
        self.tags.clear()
        for cont_tag in self.cont_tags:
            self.tags.append(cont_tag.ti_tag.get_value())

    def on_bt_add_pressed(self, widget):
        self.tags.append("")
        ti_tag = self.addTiTag("",len(self.tags) - 1)    
        self.tagsContainer.append(ti_tag)

    def on_dd_api_change(self, widget, value):
        self.api = value
        self.url = None # force load new URL
        self.imageb = None # reset the downloaded image
        self.pages = self.app.cfg[PLUGIN_NAME].PAGES #has to be re-read from config
        self.reload()
        
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
    pluginImgLoaderE.api = app.cfg[PLUGIN_NAME].API
    pluginImgLoaderE.prepare()
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

@plugins.hookimpl
def saveCfg(app) -> None:
    """called before startup
    Placeholder for plugin settings to be stored.
    Use app.saveCfg(PLUGIN_NAME, dict_with_config)
    """
    app.saveCfg(PLUGIN_NAME, 
        {"API": pluginImgLoaderE.api,
            "TAGS": pluginImgLoaderE.tags, 
        }) 