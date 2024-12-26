import random
import logging as LOGGER
import os
from loadimg import ImgLoader

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
        
    def loadFile(self, imgPath) :
        if imgPath:
            ...
            # not done yet
            #picture
    
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

