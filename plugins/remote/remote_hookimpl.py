import plugins
import remote
import logging as LOGGER
PLUGIN_NAME = "REMOTE"


class Remote:
    serverApp : remote.RemoteWeb = None

    def start(self, app):
        self.app = app
        remote.startWeb(caller=self, address=app.cfg[PLUGIN_NAME].address, port=int(app.cfg[PLUGIN_NAME].port))

    def on_init(self, serverApp : remote.RemoteWeb):
        """called from remote.RemoteWeb main after initialisation
        Place for setting initail values on the web
        """
        self.serverApp = serverApp
        remote.delayTxtFB(self.app.delay)
        remote.brightnessFB(self.app.brightness)
    
    def on_bt_nightmode_pressed(self, widget):
        if hasattr(self.app,"nightmode"):
            self.app.nightmode.forcedNightMode = not self.app.nightmode.forcedNightMode
            text = 'Day Mode' if self.app.nightmode.forcedNightMode else 'Night Mode'
            remote.nightmodeSetText(text)

    def on_brightness_changed(self, widget, value):
        self.app.setBrightness(int(value))
        self.app.show()

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


    def showFile(self,fileName):
        try:
            with open(fileName,"rb") as picture:
                LOGGER.debug(f"Loaded {picture}")
                if self.app.loadImg(buffer=picture):
                    self.app.show()
        except:
            LOGGER.error(f"{fileName} can't be read!")
    def fileupload_on_success(self,widget, fileName):
        self.showFile(fileName)

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

