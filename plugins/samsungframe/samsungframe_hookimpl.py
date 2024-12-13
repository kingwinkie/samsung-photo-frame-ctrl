import plugins
import resize
import frame_ctrl
import time
import slideshow
from loadimg import ImgLoader
from PIL import Image

def sendToFrame(img : Image):
    ret : bool = False
    buffer : bytes = resize.imgToBytes(img)
    if buffer:
        while not ret:
            ret = frame_ctrl.showImage(buffer)
            if not ret:
                time.sleep(5) #the frame is not in monitor mode, has been disconnected etc.
    return ret


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
def imageChangeBefore(app : slideshow.SlideShow):
     """called before a new image is required
    Returns ImgLoader desc. object.
    """

@plugins.hookimpl
def showImage(app : slideshow.SlideShow) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """
    return sendToFrame(app.image)