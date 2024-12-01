import plugins
from imgfolderloader import ImgLoaderFolder
from loadimg import ImgLoader
import loaderconfig

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
    imgLoader = ImgLoaderFolder(loaderconfig.IMG_SOURCE_PATH, imgExt=loaderconfig.IMG_EXT)
    return imgLoader