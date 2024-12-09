import pluggy
import slideshow
from loadimg import ImgLoader

hookspec = pluggy.HookspecMarker("slideshow")


@hookspec
def imageChangeAfter(app : slideshow.SlideShow) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc.
    """

@hookspec
def startup(app : slideshow.SlideShow) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """

@hookspec
def exit(app : slideshow.SlideShow) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """

@hookspec
def imageLoader(app : slideshow.SlideShow) -> ImgLoader:
    """creates imageLoaderClass. Remove it and move it to startup!
    Returns ImgLoader desc. object.
    """

@hookspec
def loadImage(app : slideshow.SlideShow) -> bytes:
    """called when a new image is required
    Returns bytes
    """

@hookspec
def imageChangeBegore(app : slideshow.SlideShow):
     """called before a new image is required
    Returns ImgLoader desc. object.
    """

@hookspec
def showImage(app : slideshow.SlideShow) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """