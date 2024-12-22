import plugins
import remote
import logging as LOGGER
import qrcode
import getips
import remi
from imgutils import drawText, HAlign, VAlign
PLUGIN_NAME = "REMOTE"


class Remote:
    serverApp : remote.RemoteWeb = None
    serverUrl : str # URL of the server
    initialRun : bool = True #for showing the QR code. 
    fileName : str #name of the last file
    def start(self, app):
        self.app = app
        address = app.cfg[PLUGIN_NAME].address
        port = int(app.cfg[PLUGIN_NAME].port)
        if address in ["*", "", None]:
            addrList = getips.getIPList()
            if addrList and len(addrList) > 0: 
                address = addrList[0]
        self.serverUrl = f"http://{address}:{port}"
        remote.startWeb(caller=self, address=address, port=port)
    def createRemote(self) -> list[list[remi.Widget]]:
        return self.app.createRemote()
    def on_init(self, serverApp : remote.RemoteWeb):
        """called from remote.RemoteWeb main after initialisation
        Place for setting initail values on the web
        """
        self.serverApp = serverApp
        remote.delayTxtFB(self.app.delay)
        remote.brightnessFB(self.app.brightness)
    
    def update(self, func, **kwargs):
        return self.serverApp.update(func, **kwargs)


    def on_brightness_changed(self, widget, value):
        self.app.setBrightness(int(value))
        self.app.setStage(self.app.Stage.RESIZE)

    def setBrightnessFB(self, brightness : int):
            remote.brightnessFB(brightness)

    def on_bt_load_pressed(self, widget):
        self.app.forceLoad = True

    def on_bt_pause_pressed(self, widget):
        self.app.paused = not self.app.paused
        text = "Continue" if self.app.paused else "Pause"
        remote.pausedSetText(text)

    def on_delayTxt_changed(self, widget, value):
        self.app.delay = float(value)


    def showFile(self,fullpath, fileName):
            if self.app.load(fullpath): #lazy !!!
                self.app.remotelyUploaded = True #informs other plugins that the picture has been remotely uploaded
                self.fileName = fileName
                self.app.setStage(self.app.Stage.LOAD)
                
    def fileupload_on_success(self,widget, fullpath, fileName):
        self.showFile(fullpath, fileName)

    def on_file_upload_input(self, widget, file_list):
        # Get the uploaded file
        uploaded_file = file_list[0]
        self.showFile(uploaded_file)


@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """

@plugins.hookimpl 
def imageLoader(app):
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
    if app.remote.initialRun:
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
    # add image name
    if app.remotelyUploaded and app.remote.fileName:
        text=f"{app.remote.fileName}"
        app.image = drawText(text=text, size=app.cfg.FRAME.IMG_SIZE, fontSize=12, textColor=(192,192,192,192), align=(HAlign.RIGHT, VAlign.BOTTOM), bgImage=app.image, offset=(10,5))


@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    app.remote = Remote()
    app.remote.start(app)

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
    app.remote.setBrightnessFB(brightness)

