import requests
import random
import time
from loadimg import ImgLoader

class ArtsyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()
        self.nextURL = "https://api.artsy.net/api/artworks"

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
    def __init__(self, artsy_api):
        self.artsy_api = artsy_api

    def getRandomImageURL(self) -> str:
        artworks = self.artsy_api.get_artworks()
        random_artwork = random.choice(artworks)
        image_url = random_artwork["_links"]["image"]["href"].replace("{image_version}","large")
        return image_url
        

class ImgLoaderArtsy(ImgLoader):
    downloader : RandomImageDownloader
    imageb : bytes
    downloadLimit : int #min delay between downloads
    lastDownloadAttempt : int #timestamp of the latest download attempt

    def __init__(self, client_id : str, client_secret : str):
        artsyAPI = ArtsyAPI(client_id=client_id, client_secret=client_secret)
        self.downloader = RandomImageDownloader(artsyAPI)
        self.imageb = None
        self.downloadLimit = 10
        self.lastDownloadAttempt = 0
        self.prepare()

    def prepare(self):
        """
        Informs loader that a new image will be requested (for slow downloads) 
        """
        self.imageb = None
        self.lastDownloadAttempt = time.time()
        url : str = self.downloader.getRandomImageURL()
        self.imageb = self.loadImgCURL( url )

    def load(self):
        """
        Load (return) the image
        """
        imageb = self.imageb
        self.imageb = None
        return imageb

    def isReady(self):
        """
        Tells caller if the image is ready. Intended use is for URL (slow) download.
        """
        return True if self.imageb else False
    
    def nextAttempt(self) -> float:
        now = time.time()
        delta = now - self.lastDownloadAttempt
        return self.downloadLimit - delta
    
    def areWeSafe(self) -> bool:
            return self.nextAttempt() <=0