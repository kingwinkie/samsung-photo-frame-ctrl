import plugins
from imgurlloader import ImgLoaderURL
from loadimg import ImgLoader
import loaderconfig as loaderconfig

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
    imgLoader = ImgLoaderURL(loaderconfig.IMG_SOURCE_PATH)
    return imgLoader