import pycurl, certifi
import logging as LOGGER
import io
import time

class ImgLoader:
    lastDownloadAttempt : float = 0 # last attempt to download a file
    downloadLimit : float = 10 # Min delay between downloads for not to ban us.
    imageb : bytes = None # Image prepared as bytes or ByteIO to be loaded via load()

    def prepare(self):
        """
        Informs loader that a new image will be requested (for slow downloads) 
        """
        ...
    def load(self):
        """
        Load (return) the image
        """
        if not self.imageb:
            self.prepare() # force load when image is not available
        imageb = self.imageb
        self.imageb = None
        return imageb

    def isReady(self):
        """
        Tells the caller if the image is ready. Intended use is for URL (slow) download.
        """
        return True if self.imageb else False
    
    def loadImgCURL(self, url):
        """Download routine"""
        if not url:
            return None
        imgFile = io.BytesIO()
        try:
            c = pycurl.Curl()
            c.setopt(c.TIMEOUT, 30)
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, imgFile)
            c.setopt(c.CAINFO, certifi.where())
            c.setopt(c.FOLLOWLOCATION, True) # follow redirect
            # Error code: 1010 issue
            custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']
            c.setopt(c.HTTPHEADER, custom_headers)
            LOGGER.debug(f"Downloading {url}")
            c.perform()
            c.close()
            
            LOGGER.debug(f"Image downloaded")
        except pycurl.error as e:
            LOGGER.error(f"Downloading Error: {e}")
            return None
        return imgFile
    
    def nextAttempt(self) -> float:
        """Returns time to next download atempt"""
        now = time.time()
        delta = now - self.lastDownloadAttempt
        return self.downloadLimit - delta
    
    def areWeSafe(self) -> bool:
            """Returns if downloading through prepare() can be proceen"""
            return self.nextAttempt() <=0
    
    def do(self):
        """Called from plugin do(). For image preparation"""
        if self.areWeSafe(): #time test from last download
            if self.isReady() == False:
                self.prepare()