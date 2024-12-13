import plugins
from plugins.loadimgartsy.imgaloader import ImgLoaderE621
from loadimg import ImgLoader

PLUGIN_NAME = "LOADIMGE621"

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
    imgLoader = ImgLoaderE621()
    imgLoader.pages = app.cfg.LOADIMGE621.PAGES
    imgLoader.api = app.cfg.LOADIMGE621.API
    imgLoader.tags = app.cfg.LOADIMGE621.TAGS
    imgLoader.downloadLimit = app.cfg.LOADIMGE621.HTTP_DOWNLOAD_LIMIT
    app.pluginImgLoaderE = imgLoader
    imgLoader.url = imgLoader.getURL() #download first URL
    return imgLoader

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
    imgLoader : ImgLoaderE621 = app.pluginImgLoaderE
    if imgLoader.areWeSafe(): #time test from last download
        if not imgLoader.url:
            imgLoader.url = imgLoader.getURL() #prepare URL on backfround
        