import io
import logging as LOGGER
import loadimg
import pycurl
import certifi
import time
import loaderconfig

class ImgLoaderURL(loadimg.ImgLoader):
    def __init__(self, url ):
        super().__init__()
        self.url = url
        self.lastDownloadAttempt = 0

    def download(self) -> io.BytesIO:
        now = time.time()
        delta = now - self.lastDownloadAttempt
        if delta < loaderconfig.HTTP_DOWNLOAD_LIMIT: # don't spam the server too often
            wait = loaderconfig.HTTP_DOWNLOAD_LIMIT - delta
            LOGGER.debug(f"slowdown {wait}")
            time.sleep(wait)
        self.lastDownloadAttempt = time.time()
        imgFile = io.BytesIO()
        try:
            c = pycurl.Curl()
            c.setopt(c.TIMEOUT, 30)
            c.setopt(c.URL, self.url)
            c.setopt(c.WRITEDATA, imgFile)
            c.setopt(c.CAINFO, certifi.where())
            c.setopt(c.FOLLOWLOCATION, True) # follow redirect
            # Error code: 1010 issue
            custom_headers = ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0/8mqLkJuL-86']
            c.setopt(c.HTTPHEADER, custom_headers)
            LOGGER.debug(f"Downloading {self.url}")
            c.perform()
            c.close()
            
            LOGGER.debug(f"Image downloaded")
        except pycurl.error as e:
            LOGGER.error(f"Downloading Error: {e}")
            return None
        return imgFile

    
    def load(self):
        image = self.download()
        return image
    
