import plugins
import remote
import logging as LOGGER
import qrcode
import getips
import remi
import time

PLUGIN_NAME = "REMOTE"
PLUGIN_FANCY_NAME = "Remote Controller"
PLUGIN_CLASS = "REMOTE"
PLUGIN_SORT_ORDER = 1000

class Remote:
    server : remi.Server = None
    serverApp : remote.RemoteWeb = None
    serverUrl : str # URL of the server
    initialRun : bool = True #for showing the QR code. 
    startupStamp : float = 0 # QR code is visible first 60s. Set in startup. Cloed when first contact has been made
    
    def start(self, app):
        """Starts the web app"""
        self.app = app
        address = app.cfg[PLUGIN_NAME].address
        port = int(app.cfg[PLUGIN_NAME].port)
        if address in ["*", "", None]:
            addrList = getips.getIPList()
            if addrList and len(addrList) > 0: 
                address = addrList[0]
        self.serverUrl = f"http://{address}:{port}"
        self.server = remote.startWeb(caller=self, address=address, port=port)

    def createRemote(self) -> list[tuple[str,list[remi.Widget]]]:
        """returns list of GUI items from plugins"""
        return self.app.createRemote()
    def on_init(self, serverApp : remote.RemoteWeb):
        """called from remote.RemoteWeb main after initialisation
        Place for setting initail values on the web
        """
        self.serverApp = serverApp
        self.startupStamp = 0 #first connection attempt made. Closing QR code
        
    def shutdown(self):
        self.server.stop()
    
    def secureUpdate(self, func, **kwargs):
        """Thread safe update. Called from plugins"""
        if self.serverApp:
            self.serverApp.secureUpdate(func, **kwargs)

@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """
    app.remote.shutdown()
     

@plugins.hookimpl
def imageChangeBefore(app) -> None:
    """called after image was successfuly changed on the screen
    Intended for effects etc. Image is in app.image
    """
    tdelta = time.time() - app.remote.startupStamp 
    if  app.remote.startupStamp and tdelta < 60 : #shoq qr code at least first 60s
        qr = qrcode.QRCode(version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=7,
                        border=4)
        qr.add_data(app.remote.serverUrl)
        LOGGER.debug(f"QR created {app.remote.serverUrl}")
        qr.make()
        #qrcode_fill_color = '#%02x%02x%02x' % cfg.gettyped("QRCODE", 'foreground')
        #qrcode_background_color = '#%02x%02x%02x' % cfg.gettyped("QRCODE", 'background')
        qrImage = qr.make_image()
        if qrImage:
            LOGGER.debug(f"QR paste")
            app.image.paste(im=qrImage.get_image())
        else:
            LOGGER.error(f"QR creation error")
        app.remote.initialRun = False
    

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    app.remote = Remote()
    app.remote.start(app)
    app.remote.startupStamp = time.time()

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """
    defaultConfig = {
        "ADDRESS" : "localhost",
        "PORT" : "8088",
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

