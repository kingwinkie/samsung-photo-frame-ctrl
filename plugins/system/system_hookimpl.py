import plugins
import remi.gui as gui
from fastapi import APIRouter
from slideshow import SlideShow
PLUGIN_NAME = "SYSTEM" # set plugin name here. This must be the same as prefix of this file.
PLUGIN_FANCY_NAME = "System management" # set fancy name for remote controller here
PLUGIN_CLASS = "SYSTEM" # Classes are: LOADER (force load after change), DISPLAY (at least one must stay active), REMOTE(can't be unloaded from web)
PLUGIN_SORT_ORDER = 500 #Order for remote controller dialogs. Ascending.

class SystemManagement:
    app : SlideShow = None

    def btRebootOnClick(self,widget):
        self.app.quitApp(quit=True, shutdown=False, reboot=True)

    def btShutdownOnClick(self,widget):
        self.app.quitApp(quit=True, shutdown=True, reboot=False)


    def setRemote(self):
        """For setting web based remote from plugins. Returns list of remi.Widgets"""
        btReboot = gui.Button('Restart', width = 200, height = 30, margin = "4px")
        btReboot.onclick.do(self.btRebootOnClick)
        btShutdown = gui.Button('Shutdown', width = 200, height = 30, margin = "4px")
        btShutdown.onclick.do(self.btShutdownOnClick)
        return [btReboot,btShutdown]


systemManagement = SystemManagement()
@plugins.hookimpl
def setRemote(app):
    systemManagement.app = app
    return systemManagement.setRemote()



@plugins.hookimpl
def setAPI(app : SlideShow):
    """
    Placeholder for setting plugin specific REST API calls.
    Should contain:
    router = APIRouter()
    @router.get("/api_point")
        def api_point():
            return {"message": "Not implemented yet"}
    app.api.registerRouter(PLUGIN_NAME, router)
    """
    router = APIRouter()

    @router.get("/turnoff")
    def turnoff():
        app.quitApp(quit=True, shutdown=False, reboot=False)
        return {"message": f"Turning Off"}
    
    @router.get("/shutdown")
    def shutdown():
        app.quitApp(quit=True, shutdown=True, reboot=False)
        return {"message": f"Shuting Down"}
    
    @router.get("/restart")
    def restart():
        app.quitApp(quit=True, shutdown=False, reboot=True)
        return {"message": f"Restarting"}
    app.api.registerRouter(PLUGIN_NAME, router)
    
