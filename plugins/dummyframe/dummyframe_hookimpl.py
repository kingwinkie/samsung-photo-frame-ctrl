import plugins
import slideshow
import pygame

from loadimg import ImgLoader
from PIL import Image

     
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
    pygame.init()
    window_size = app.size
    app.dummyScreen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Dummy frame')

@plugins.hookimpl
def exit(app : slideshow.SlideShow) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """
    pygame.quit()

@plugins.hookimpl
def imageLoader(app : slideshow.SlideShow) -> ImgLoader:
    """called when a new image is required
    Returns ImgLoader desc. object.
    """

@plugins.hookimpl
def imageChangeBegore(app : slideshow.SlideShow):
     """called before a new image is required
    Returns ImgLoader desc. object.
    """

@plugins.hookimpl
def showImage(app : slideshow.SlideShow) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """
    if app.image:
        image_data = app.image.tobytes()
        image_size = app.image.size
        pygame_surface = pygame.image.frombytes(image_data, image_size, 'RGB')
        app.dummyScreen.blit(pygame_surface, (0, 0))
        # Update the display
        pygame.display.flip()
        return True