import io
import logging as LOGGER
import loadimg
import time

class ImgLoaderURL(loadimg.ImgLoader):
    def __init__(self, url, downloadLimit : float ):
        super().__init__()
        self.url = url
        self.downloadLimit = downloadLimit
        self.lastDownloadAttempt = 0

    def download(self) -> io.BytesIO:
        now = time.time()
        delta = now - self.lastDownloadAttempt
        if delta < self.downloadLimit: # don't spam the server too often
            wait = self.downloadLimit - delta
            LOGGER.debug(f"slowdown {wait}")
            time.sleep(wait)
        self.lastDownloadAttempt = time.time()
        return self.loadImgCURL( self.url )
        
    
    def load(self) -> bytes:
        image = self.download()
        return image
    
