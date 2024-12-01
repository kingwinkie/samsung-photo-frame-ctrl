import pluggy
from loadimg import ImgLoader

hookspec = pluggy.HookspecMarker("slideshow")


@hookspec
def imageChangeAfter(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc.
    """

@hookspec
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """

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