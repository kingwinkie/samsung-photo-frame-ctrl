import random
import os.path as osp
import logging as LOGGER

from loadimg import ImgLoader

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request  # Import added

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

class GPDownloader(ImgLoader):
    mediaItems : list = []
    description : str = None
    nextPageToken : str = None
    counter : int = 0
    def authenticate(self):
        tokenPath = osp.join(osp.realpath(osp.dirname(__file__)), ".secrets.token.json")
        credPath = osp.join(osp.realpath(osp.dirname(__file__)), ".secrets.credentials.json")
        
        creds = None
        if osp.exists(tokenPath):
            creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credPath, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(tokenPath, 'w') as token:
                token.write(creds.to_json())
        return creds

    def getList(self):
        """Get a list of media items from the user"""
        creds = self.authenticate()
        service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
        results = service.mediaItems().list(pageSize=100, pageToken=self.nextPageToken).execute()
        self.mediaItems = results.get('mediaItems', [])
        self.nextPageToken = results.get('nextPageToken', None)
        if not self.mediaItems:
            LOGGER.error('No media items found.')
        
    def prepare(self):
        if self.counter%50 == 0:
            self.getList()
        self.counter += 1
        if self.mediaItems:
            random_item = random.choice(self.mediaItems)
            image_url = random_item['baseUrl']
            self.description = random_item['filename']
            self.imageb = self.loadImgCURL(image_url)
    
        
if __name__ == '__main__':
    gpApi = GPDownloader()
    gpApi.prepare()