import plugins
from imgeloader import ImgLoaderE621
from loadimg import ImgLoader
import loadereconfig as loaderconfig

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
    return imgLoader