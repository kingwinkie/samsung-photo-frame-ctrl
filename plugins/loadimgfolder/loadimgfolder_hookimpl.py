import plugins
from imgfolderloader import ImgLoaderFolder
from loadimg import ImgLoader
import loaderconfig
from loadimg import ImgLoader
import slideshow

@plugins.hookimpl
def showImage(app : slideshow.SlideShow) -> bool:
     """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """
     
@plugins.hookimpl
def imageChangeAfter(app : slideshow.SlideShow) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc.
    """

@plugins.hookimpl
def startup(app : slideshow.SlideShow) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    app.imgLoaderFolder = ImgLoaderFolder(loaderconfig.IMG_SOURCE_PATH, imgExt=loaderconfig.IMG_EXT)

@plugins.hookimpl
def exit(app : slideshow.SlideShow) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """

@plugins.hookimpl
def imageLoader(app : slideshow.SlideShow) -> ImgLoader:
    """called when a new image is required
    Returns ImgLoader desc. object.
    """
    


@plugins.hookimpl
def loadImage(app : slideshow.SlideShow) -> bytes:
    """called when a new image is required
    Returns bytes
    """
    if hasattr(app, "imgLoaderFolder") and app.imgLoaderFolder:
        return app.imgLoaderFolder.load()

@plugins.hookimpl
def imageChangeBegore(app : slideshow.SlideShow):
    """called before a new image is required
    Returns ImgLoader desc. object.
    """

@plugins.hookimpl
def showImage(app : slideshow.SlideShow) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """
    