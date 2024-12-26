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
        self.description : str = None #Current art description
        
    

    def get_token(self):
        url = "https://api.artsy.net/api/tokens/xapp_token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()["token"]

    def get_artworks(self):
        
        headers = {
            "X-Xapp-Token": self.token
        }
        response = requests.get(self.nextURL, headers=headers)
        response.raise_for_status()
        jsonResponse = response.json()
        artworks = jsonResponse["_embedded"]["artworks"]
        self.nextURL = jsonResponse["_links"]["next"]["href"]
        return artworks

class RandomImageDownloader:
    def __init__(self, artsy_api, size):
        self.artsy_api = artsy_api
        self.size = size

    def getRandomArtwork(self) -> str:
        artworks = self.artsy_api.get_artworks()
        random_artwork = random.choice(artworks)
        return random_artwork
        

class ImgLoaderArtsy(ImgLoader):
    downloader : RandomImageDownloader
    
    def __init__(self, client_id : str, client_secret : str, size : tuple[int,int]):
        artsyAPI = ArtsyAPI(client_id=client_id, client_secret=client_secret)
        self.downloader = RandomImageDownloader(artsyAPI, size)
        self.size = size
        self.prepare()

    def prepare(self):
        """
        Informs loader that a new image will be requested (for slow downloads) 
        """
        try:
            self.imageb = None
            self.lastDownloadAttempt = time.time()
            self.artwork : dict = self.downloader.getRandomArtwork()
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
        if not self.imageb:
            self.prepare() # force load when image is not available
        
        imageb = self.imageb
        self.description=f"{self.artwork['slug']} ({self.artwork['date']})"

        self.imageb = None
        return imageb


    