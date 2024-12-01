class ImgLoader:

    def prepare(self):
        """
        Informs loader that a new image will be requested (for slow downloads) 
        """
        ...
    def load(self):
        """
        Load (return) the image
        """
        ...

    def isReady(self):
        """
        Tells caller if the image is ready. Intended use is for URL (slow) download.
        """
        return False