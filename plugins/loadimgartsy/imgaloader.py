import requests
import random
import time
from loadimg import ImgLoader
import logging as LOGGER

class ArtsyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()
        self.nextURL = "https://api.artsy.net/api/artworks"
        self.artwork : dict = None
        self.minAR : float = 0 #Minimum aspect ratio for images to download

    def get_token(self):
        url = "https://api.artsy.net/api/tokens/xapp_token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()["token"]

    def filterAR(self, width : int, height : int):
        if self.minAR:
            try:
                return width/height > self.minAR
            except:
                return False
        return True #AR 0 = always valid
    
    def get_artworks(self):
        artworks = None
        headers = {
            "X-Xapp-Token": self.token
        }
        response = requests.get(self.nextURL, headers=headers)
        response.raise_for_status()
        jsonResponse = response.json()
        artworks = jsonResponse["_embedded"]["artworks"]
        self.nextURL = jsonResponse["_links"]["next"]["href"]
        if artworks:
            artworks = filter(lambda x: self.filterAR(x["dimensions"]["cm"]["width"],x["dimensions"]["cm"]["height"]), artworks)
            artworks = list(artworks)
            LOGGER.info(f"Found zero images with AR > {self.minAR}.")
        return artworks

class RandomImageDownloader:
    def __init__(self, artsy_api, size):
        self.artsy_api = artsy_api
        self.size = size

    def getRandomArtwork(self) -> str:
        artworks = self.artsy_api.get_artworks()
        if artworks:
            random_artwork = random.choice(artworks)
            return random_artwork
        
class ImgLoaderArtsy(ImgLoader):
    downloader : RandomImageDownloader
    
    def __init__(self, client_id : str, client_secret : str, size : tuple[int,int]):
        self.artsyAPI = ArtsyAPI(client_id=client_id, client_secret=client_secret)
        self.downloader = RandomImageDownloader(self.artsyAPI, size)
        self.size = size
        self.description : str = None #Current art description
        self.prepare()
    
    @property
    def minAR(self):
        return self.artsyAPI.minAR
    
    @minAR.setter
    def minAR(self,value):
        self.artsyAPI.minAR = value
    
    def prepare(self):
        """
        Informs loader that a new image will be requested (for slow downloads) 
        """
        try:
            self.imageb = None
            self.lastDownloadAttempt = time.time()
            artwork : dict = self.downloader.getRandomArtwork()
            if artwork:
                self.artwork = artwork
                try:
                    url = self.artwork["_links"]["image"]["href"].replace("{image_version}","large")
                except KeyError as e:
                    LOGGER.error(f"Arkwork URL key error {e}")
                    return None
                self.imageb = self.loadImgCURL( url )
        except requests.exceptions.ConnectionError as connError:
            LOGGER.error(f"Image downloading error {connError}")

    def load(self):
        """
        Load (return) the image
        """
        imageb = super().load()
        if imageb:
            self.description=f"{self.artwork['slug']} ({self.artwork['date']})"
        return imageb


    