import plugins
import remote
import logging as LOGGER
import qrcode
import getips
import remi
import plugins
from imgutils import drawText, HAlign, VAlign
PLUGIN_NAME = "REMOTE"
PLUGIN_FANCY_NAME = "Remote Controller"
PLUGIN_CLASS = "REMOTE"
PLUGIN_SORT_ORDER = 1000

class Remote:
    server : remi.Server = None
    serverApp : remote.RemoteWeb = None
    serverUrl : str # URL of the server
    initialRun : bool = True #for showing the QR code. 
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

    def shutdown(self):
        self.server.stop()
    
    def secureUpdate(self, func, **kwargs):
        """Thread safe update. Called from plugins"""
        if self.serverApp:
            self.serverApp.secureUpdate(func, **kwargs)

    def getPluginsContainer(self) -> remi.gui.Container:
        """Container with list of plugins and on/off checkboxes"""
        container = None
        pl = self.app.pm.getAvailablePlugins()
        if pl:
            container = remi.gui.Container(width=320, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center', 'border-color': 'gray', 'border-width': '2px', 'border-style': 'solid','margin': '4px', 'padding': '2px'})
            label = remi.gui.Label("Plugins", height=12, margin='0px', style={'color':'white','background-color':'rgb(3, 88, 200)', 'font-size':'8px', 'margin-bottom':'10px'})
            container.append(label)
            checks = []
            for enabled, plugin in pl:
                #enabled : bool = p[0]
                #plugin = p[1]
                pluginName : str = plugin.PLUGIN_NAME
                friendlyName : str = self.app.pm.getFancyName(plugin, False)
                if hasattr(plugin, "PLUGIN_SORT_ORDER"):
                    sortOrder : int = plugin.PLUGIN_SORT_ORDER
                else:
                    sortOrder = 0
                    
                if hasattr(plugin, "PLUGIN_CLASS"):
                    if plugin.PLUGIN_CLASS in ["REMOTE", "DISPLAY","BASIC"]:
                        continue #ignore REMOTE
                check = remi.gui.CheckBoxLabel(friendlyName, enabled, width=300, height=20, margin='4px', style={'justify-content': 'left'})
                check.pluginName = pluginName
                check.sortOrder = sortOrder
                check.onchange.do(self.on_check_change)
                checks.append(check)
            checks.sort(key= lambda c : c.sortOrder)
            container.append(checks)    
        return container

    def on_check_change(self, widget, value):
        plugin = self.app.pm.getAvailablePlugin(widget.pluginName)
        if plugin:
            if value:
                self.app.pm.register(plugin)
                # call startup
                if hasattr(plugin, "loadCfg"):
                    plugin.loadCfg(self.app)
                if hasattr(plugin, "startup"):
                    plugin.startup(self.app)
                stage = self.app.Stage.LOAD
                if hasattr(plugin, "setRemote"):
                    self.serverApp.addPluginContainer(plugin.PLUGIN_NAME,
                                self.app.pm.getFancyName(plugin, False),
                                plugin.setRemote(app=self.app)) #call plugin
                if hasattr(plugin, "PLUGIN_CLASS"):
                    if plugin.PLUGIN_CLASS == "LOADER":
                        stage = None
                self.app.setStage(stage) #force reload
                    
            else:
                # unchecked - clean and deregister the plugin
                if hasattr(plugin, "exit"):
                    plugin.exit(app=self.app)
                self.app.pm.unregister(plugin)
                self.app.setStage(self.app.Stage.LOAD)
                self.serverApp.removePluginContainer(widget.pluginName)


        

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

