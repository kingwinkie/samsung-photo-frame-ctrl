import plugins
from nightmode import Nightmode
PLUGIN_NAME = "NIGHTMODE"
PLUGIN_FANCY_NAME = "Night Mode"
PLUGIN_SORT_ORDER = 310
nightmode = Nightmode()

def setMode():
    mode = nightmode.getMode()
    nightmode.checkTTModeChange()
    nightmode.setMode(mode)
    nightmode.lastMode = mode


@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    nightmode.srcTable = app.cfg[PLUGIN_NAME].TIMES
    nightmode.createTT(nightmode.srcTable)
    nightmode.app = app
    nightmode.nightBrightness = app.cfg[PLUGIN_NAME].NIGHT_BRIGHTNESS
    nightmode.lastMode = Nightmode.MODE.DAY

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """
    defaultConfig = {
        "NIGHT_BRIGHTNESS" : 10,
        "TIMES" : [("07:00", "day"),("22:00", "night")]
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

@plugins.hookimpl
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """
    nightmode.checkTTModeChange()
    if nightmode.lastMode != nightmode.getMode():
        setMode()


@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""
    return nightmode.setRemote()
    