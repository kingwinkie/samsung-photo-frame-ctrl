import pluggy
import slideshow
from loadimg import ImgLoader

hookspec = pluggy.HookspecMarker("slideshow")


@hookspec
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """

@hookspec 
def imageLoader(app) -> ImgLoader:
    """called when a new image is required
    Returns ImgLoader desc. object.
    """

@hookspec
def imageChangeAfter(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """

@hookspec
def imageChangeBefore(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """

@hookspec
def startup(app : slideshow.SlideShow) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """

@hookspec
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """

@hookspec
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """
