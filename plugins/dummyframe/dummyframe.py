import pygame
import threading
from PIL import Image
from slideshow import SlideShow

class DummyFrame:
    display : pygame.Surface
    displayThread : threading.Thread
    window_size : tuple[int,int]
    image : Image
    app : SlideShow

    def __init__(self, app : SlideShow):
        self.window_size = app.cfg.FRAME.IMG_SIZE
        self.displayThread = threading.Thread(target=self.runner, daemon=True)
        self.displayThread.start()
        self.image = None
        self.app = app
    def __del__(self):
        pygame.quit()

    def runner(self):
        pygame.init()
        self.display = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Dummy frame')

        running = True
        while running:
            if self.image:
                self.showImage(self.image)
                self.image = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
        if not running:
            self.app.quitApp()

    def showImage(self,image : Image):
        """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
        """
        if image:
            image_data = image.tobytes()
            image_size = image.size
            pygame_surface = pygame.image.frombytes(image_data, image_size, 'RGB')
            self.display.blit(pygame_surface, (0, 0))
            # Update the display
            pygame.display.flip()

    def setImage(self, image : Image):
        self.image = image
