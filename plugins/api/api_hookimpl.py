import plugins
PLUGIN_NAME = "API" # set plugin name here. This must be the same as prefix of this file.
PLUGIN_FANCY_NAME = "Rest API" # set fancy name for remote controller here
PLUGIN_CLASS = "SYSTEM" # Classes are: LOADER (force load after change), DISPLAY (at least one must stay active), REMOTE(can't be unloaded from web)
PLUGIN_SORT_ORDER = 510 #Order for remote controller dialogs. Ascending.
from fastapi import FastAPI, APIRouter
import logging as LOGGER
import uvicorn
import getips
import asyncio
import threading
from fastapi import APIRouter
from slideshow import SlideShow

class API:
    fastAPIApp : FastAPI
    loop : asyncio.BaseEventLoop = None
    app : SlideShow = None
    def startup(self, app, address : str = None, port : int = 8000):
        self.fastAPIApp = FastAPI()
        self.address = address
        self.port = port
        if address in ["*", "", None]: #assign real IP address. For use on RPi
            addrList = getips.getIPList()
            if addrList and len(addrList) > 0: 
                address = addrList[0]

        @self.fastAPIApp.get("/")
        def hello_world():
            """API is alive"""
            return {"message": "Hakuna matata!"}
        
        app.createAPI() # calls plugin before starting the server @self.router.get("/...") are there
        self.start_server() 
    
    def start_server(self):
        """Start FastAPI server in it's own thread"""
        self.loop = asyncio.new_event_loop()
        self.serverThread = threading.Thread(target=self.run_server, args=(self.loop,), name="uvicorn")
        self.serverThread.start()

    def run_server(self, loop):
        """Thread runner"""
        asyncio.set_event_loop(loop)
        config = uvicorn.Config(self.fastAPIApp, host=self.address, port=self.port, reload=True,log_level='error')
        self.server = uvicorn.Server(config)
        loop.run_until_complete(self.server.serve())
        
    def _set_should_exit(self):
        """Thread safe exit"""
        self.server.should_exit = True

    def stop_server(self):
        """Stop the server from main app"""
        if self.server and self.loop:
            self.loop.call_soon_threadsafe(self._set_should_exit)
    
    def registerRouter(self,prefix : str, router : APIRouter):
        """
        Called from plugins.
        Registers plugin into API - adds the plugin specific route
        """
        if prefix[1] != "/" :
            prefix = "/" + prefix
        
        LOGGER.debug(f"registering {prefix}")
        self.fastAPIApp.include_router(router, prefix=prefix)
        return router
    
# === Hookimpls ===

@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """
    app.api.stop_server()

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    if not hasattr(app,'api') or (hasattr(app,'api') and app.api is None):
        api = API()
        app.api = api
        api.startup(app, address=app.cfg[PLUGIN_NAME].address, port=app.cfg[PLUGIN_NAME].port)
        
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

