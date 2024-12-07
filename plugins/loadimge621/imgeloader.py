import io
import logging as LOGGER
import loadimg
import pycurl
import certifi
import time
import loadereconfig
import py621
import random

class ImgLoaderE621(loadimg.ImgLoader):
    def __init__(self):
        super().__init__()
        self.lastDownloadAttempt = 0
        self.pages = loadereconfig.PAGES

    def download(self, url : str) -> io.BytesIO:
        self.waitUntilWeReSafe()
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

    def getURL(self) -> str:
        # Create an unsafe api instance
        api_type = getattr(loadereconfig,"API")
        api = py621.public.api(api_type)
        page : int = random.randint(0, self.pages)

        #choose a random post
        perpages = 70
        

        # Get posts from the Pool object
        posts = api.getPosts(loadereconfig.TAGS,70,page,False) #negative tags don't work with True
        end : int = len(posts)
        LOGGER.debug(f"Found {end} posts")

        if end:
            imageNr : int = random.randint(0, end-1)
            LOGGER.debug(f"ImageNr: {imageNr}")

            post = posts[imageNr] # Select a post from the pool
            return post.sample.url
        else:
            # pages may be missing. Decrease the range
            if page > 1:
                self.pages = page - 1
                LOGGER.debug(f"Nr. of pages decreased to  {self.pages}")

    def waitUntilWeReSafe(self):
        now = time.time()
        delta = now - self.lastDownloadAttempt
        if delta < loadereconfig.HTTP_DOWNLOAD_LIMIT: # don't spam the server too often
            wait = loadereconfig.HTTP_DOWNLOAD_LIMIT - delta
            LOGGER.debug(f"slowdown {wait}")
            time.sleep(wait)
        self.lastDownloadAttempt = time.time()

    def load(self):
        self.waitUntilWeReSafe()
        url : str = self.getURL()
        if url:
            image = self.download(url)
            return image
    
