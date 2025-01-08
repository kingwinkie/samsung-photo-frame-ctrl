import plugins
PLUGIN_NAME = "API" # set plugin name here. This must be the same as prefix of this file.
PLUGIN_FANCY_NAME = "Rest API" # set fancy name for remote controller here
PLUGIN_CLASS = "SYSTEM" # Classes are: LOADER (force load after change), DISPLAY (at least one must stay active), REMOTE(can't be unloaded from web)
PLUGIN_SORT_ORDER = 510 #Order for remote controller dialogs. Ascending.
from fastapi import APIRouter, Depends, HTTPException, status
#import logging as LOGGER
import uvicorn
import getips
import asyncio
import threading
from slideshow import SlideShow
gapp : SlideShow = None 
class API:
    router : APIRouter = APIRouter()
    loop : asyncio.BaseEventLoop = None
    app : SlideShow = None
    def startup(self, app, address : str = None, port : int = 8000):
        global gapp
        gapp = app
        self.router = APIRouter()
        self.address = address
        self.port = port
        self.app = app
        if address in ["*", "", None]:
            addrList = getips.getIPList()
            if addrList and len(addrList) > 0: 
                address = addrList[0]


        @self.router.get("/")
        def hello_world():
            return {"message": "Hakuna matata!"}
        
        @self.router.get("/load")
        def load():
            gapp.setStage(None)
            return {"message": "Loading new image"}
        
        self.app.createAPI(self.router) # calls plugin before starting the server @self.router.get("/...") are there
        self.start_server() 
    
    def start_server(self):
        self.loop = asyncio.new_event_loop()
        self.serverThread = threading.Thread(target=self.run_server, args=(self.loop,), name="uvicorn")
        self.serverThread.start()

    def run_server(self, loop):
        asyncio.set_event_loop(loop)
        config = uvicorn.Config(self.router, host=self.address, port=self.port, reload=True,log_level='error')
        self.server = uvicorn.Server(config)
        loop.run_until_complete(self.server.serve())
        
    def _set_should_exit(self):
        self.server.should_exit = True
    def stop_server(self):
        if self.server and self.loop:
            self.loop.call_soon_threadsafe(self._set_should_exit)
        

    
   


api = API()
@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """
    api.stop_server()

@plugins.hookimpl 
def load(app):
    """called when a new image is required
    Returns ImgLoader desc. object.
    """

@plugins.hookimpl
def imageChangeAfter(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """

@plugins.hookimpl
def imageChangeBefore(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    if not hasattr(app,'api') or (hasattr(app,'api') and app.api is None):
        api.startup(app, address=app.cfg[PLUGIN_NAME].address, port=app.cfg[PLUGIN_NAME].port)
        app.api = api
    

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """
    defaultConfig = {
        "ADDRESS" : "localhost",
        "PORT" : "8000",
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

@plugins.hookimpl
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """


@plugins.hookimpl
def showImage(app) -> bool:
    """called when a new image should be shown. Intended use is for display plugins. Returns success or failure.
    """

@plugins.hookimpl
def imageChangeBeforeEffects(app):
    """For post-effects aka NightMode. Called after imageChangeBefore and before showImage. Intended use is for global filters.
    """
    
@plugins.hookimpl
def brightnessChangeAfter(app, brightness : int) -> None:
    """called after brightness value was changed. Brightness is 0-255
    Intended as a feedback for remote
    """

@plugins.hookimpl
def ResizeBefore(app):
    """Called before resize"""

@plugins.hookimpl
def ResizeAfter(app):
    """Called after resize"""

@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""

@plugins.hookimpl
def loadAfter(app):
    """Called after successful load"""