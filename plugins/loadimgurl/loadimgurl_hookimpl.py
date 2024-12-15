import plugins
from imgurlloader import ImgLoaderURL
from loadimg import ImgLoader

PLUGIN_NAME="LOADIMGURL"

@plugins.hookimpl
def imageLoader(app) -> ImgLoader:
    imgLoader = ImgLoaderURL(app.cfg[PLUGIN_NAME].IMG_SOURCE_PATH, app.cfg[PLUGIN_NAME].HTTP_DOWNLOAD_LIMIT)
    return imgLoader

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
        "DELAY" : 10 # how long show the picture without any effects in second
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)

