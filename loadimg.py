import pycurl, certifi
import logging as LOGGER
import io

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
    
    def loadImgCURL(self, url):
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