import pygame
import threading
import logging as LOGGER
from PIL import Image
from slideshow import SlideShow

class DummyFrame:
    display : pygame.Surface
    displayThread : threading.Thread
    window_size : tuple[int,int]
    image : Image
    app : SlideShow

    def __init__(self, app : SlideShow):
        self.window_size = app.frameSize
        self.displayThread = threading.Thread(target=self.runner, daemon=True)
        self.displayThread.start()
        self.image = None
        self.app = app
        self.UE_NEW_IMG = pygame.event.Event(pygame.event.custom_type())
    
    def __del__(self):
        pygame.quit()

    def runner(self):
        """Pygame event thread"""
        pygame.init() # must be started in the thread
        
        self.display = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Dummy frame')
        running = True
        self.showImage(self.image) #show the intial image if it exists
        while running:
            event = pygame.event.wait()
            if event.type == self.UE_NEW_IMG.type:
                self.showImage(self.image)
            elif event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        self.app.quitApp()

    def pilImg2Surface(self,image : Image) -> pygame.Surface:
        """converts PIL image to pygame image"""
        if image:
            image_data = image.tobytes()
            return pygame.image.frombytes(image_data, image.size, 'RGB')

    def showSurface(self,pgSurface : pygame.Surface):
        """updates the display"""
        if pgSurface:
            self.display.blit(pgSurface, (0, 0))
            pygame.display.flip()
            LOGGER.debug("ChangeImg Done")

    def showImage(self,image : Image):
        """shows PIL image. Called from inside the thread"""
        pgSurface = self.pilImg2Surface(image)
        self.showSurface(pgSurface)

    def setImage(self, image : Image):
        """Changes the image. Called from outside of the thread"""
        self.image = image
        pygame.event.post(self.UE_NEW_IMG)
        LOGGER.debug("ChangeImg Request")