import plugins
import slideshow
import dummyframe
PLUGIN_NAME = "DUMMYFRAME"
PLUGIN_FANCY_NAME = "Dummy Frame"
PLUGIN_CLASS = "DISPLAY"
PLUGIN_SORT_ORDER = 500
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
    app.dummyScreen = dummyframe.DummyFrame(app)

@plugins.hookimpl
def exit(app : slideshow.SlideShow) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """
    #dummyframe.pygame.quit()
    del app.dummyScreen


@plugins.hookimpl
def showImage(app : slideshow.SlideShow) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """
    app.dummyScreen.setImage( app.image)
    return True
    