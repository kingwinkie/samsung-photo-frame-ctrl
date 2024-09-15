import io
import random
import logging as LOGGER
import os
import pycurl
import certifi
import time
import config

class Randomizer:
    def __init__(self):
        self.queue= []

    def createQueue(self,limit):
        self.limit = limit
        self.newQueue()
    
    def newQueue(self):
        self.queue= []
        for i in range(0, self.limit):
            self.queue.append((random.randint(0, self.limit),i))
        self.queue.sort()
    
    def getRandom(self):
        if self.queue: #use a randomized buffer instead of a random number
            x,nr = self.queue.pop()
            if len(self.queue) == 0:
                self.newQueue() # queue is empty recreate the queue again        
        return nr
    
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

class ImgLoaderRandom(ImgLoader):
    
    def loadNr(self, nr: int):
        ...

    def getCount(self):
        ...

    def loadRandom(self):
        if self.getCount():
            nr = self.getRandomNr()
            return self.loadNr(nr)

    def getRandomNr(self):
        limit = self.getCount() - 1
        nr = random.randint(0, limit)
        return nr


class LoaderFile(): # takes random file from a folder
        
    def loadFile(self, imgPath):
        picture = None
        if not imgPath:
            return None
        try:
            picture = open(imgPath,"rb")
            LOGGER.debug(f"Loaded {imgPath}")
        except:
            LOGGER.error(f"{imgPath} can't be read!")
            return None
        return picture
    
class ImgLoaderFolder(ImgLoaderRandom): # takes random file from a folder
    
    def __init__(self, imgFolder, imgExt ):
        super().__init__()
        self.imgFolder = imgFolder
        self.imgExt = imgExt
        self.loaderFile = LoaderFile()
        self.loadFolder()

    def load(self):
        return self.loadRandom()

    def loadFolder(self):
        self.files = self.getFiles()
        self.randomizer = Randomizer()
        fcount = self.getCount()
        self.randomizer.createQueue(fcount)
        LOGGER.debug(f"LoadFolder {self.imgFolder} {fcount} files")
    
    def getRandomNr(self):
        nr = self.randomizer.getRandom()
        return nr

    def getFiles(self):
        files = []
        try:
            files = [
                f for f in os.scandir(self.imgFolder) if f.is_file() and f.name.endswith("." + self.imgExt)
            ]
        except OSError as e:
            LOGGER.error(f"Folder '{self.imgFolder}' is not accessible [{e.strerror}]")
        return files
    
    def getCount(self):
        return len(self.files)
    
    def loadNr(self, nr: int):
        files = self.getFiles()
        count = self.getCount()
        if ( nr >= 0 and nr < count):
            return self.loaderFile.loadFile(files[nr].path)

    def isReady(self):
        return True #file is always ready
    
    def isDownloading(self):
        return False

class ImgLoaderURL(ImgLoader):
    def __init__(self, url ):
        super().__init__()
        self.url = url
        self.loaderFile = LoaderFile()
        self.lastDownloadAttempt = 0

    def download(self):
        now = time.time()
        delta = now - self.lastDownloadAttempt
        if delta < config.HTTP_DOWNLOAD_LIMIT: # don't spam the server too often
            wait = config.HTTP_DOWNLOAD_LIMIT - delta
            LOGGER.debug(f"slowdown {wait}")
            time.sleep(wait)
        self.lastDownloadAttempt = time.time()
        imgFile = io.BytesIO()
        try:
            c = pycurl.Curl()
            c.setopt(pycurl.TIMEOUT, 30)
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
    
