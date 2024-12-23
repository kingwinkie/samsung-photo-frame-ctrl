import plugins
import remote
import logging as LOGGER
import qrcode
import getips
import remi
from imgutils import drawText, HAlign, VAlign
PLUGIN_NAME = "REMOTE"


class Remote:
    server : remi.Server = None
    serverApp : remote.RemoteWeb = None
    serverUrl : str # URL of the server
    initialRun : bool = True #for showing the QR code. 
    fileName : str #name of the last file
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
        self.delayTxtFB(self.app.delay)
        self.setBrightnessFB(self.app.brightness)
    
    def progress(self, value, limit):
        val = value * 100 // limit
        if self.serverApp:
            self.serverApp.secureUpdate(self.serverApp.nextLoad.set_value(val), val=val)

    def on_brightness_changed(self, widget, value):
        self.app.setBrightness(int(value))
        self.app.setStage(self.app.Stage.RESIZE)

    def setBrightnessFB(self, brightness : int):
        if self.serverApp:
            self.serverApp.secureUpdate(self.serverApp.slider_brightness.set_value( brightness ), brightness=brightness)

    def delayTxtFB(self, delay : int):
        if self.serverApp:
            self.serverApp.secureUpdate(self.serverApp.delayTxt.set_text( str(delay)), delay=delay)
    
    def pauseSetText(self, text : str):
        if self.serverApp:
            self.serverApp.secureUpdate(self.serverApp.bt_pause.set_text(text), text=text)
            

    def on_bt_load_pressed(self, widget):
        self.app.forceLoad = True

    def on_bt_pause_pressed(self, widget):
        self.app.paused = not self.app.paused
        text = "Continue" if self.app.paused else "Pause"
        self.pauseSetText(text)

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
    def shutdown(self):
        self.server.stop()
        

    def getPluginsContainer(self) -> remi.gui.Container:
        pl = self.app.pm.list_name_plugin()
        if pl:
            container = remi.gui.Container(width=320, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center', 'border-color': 'gray', 'border-width': '2px', 'border-style': 'solid','margin': '4px', 'padding': '2px'})
            label = remi.gui.Label("Plugins", height=12, margin='0px', style={'color':'white','background-color':'rgb(3, 88, 200)', 'font-size':'8px', 'margin-bottom':'10px'})
            container.append(label)
        for p in pl:
            pname = p[0]
            check = remi.gui.CheckBoxLabel(pname, True, width=200, height=30, margin='10px', style={'align-items': 'left'}, align='left')
            check.onchange.do(self.on_check_change)
            container.append(check)
        return container

    def on_check_change(self, widget, value):
        if value:
            self.app.pm.register(widget.text)
        else:
            self.app.pm.unregister(widget.text)
        self.app.setStage(self.app.Stage.LOAD)

        

@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """
    app.remote.shutdown()
     

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
    app.remote.progress(app.idleIter, int(app.delay))

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

