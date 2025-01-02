import plugins
import logging as LOGGER
import remi
PLUGIN_NAME = "PLUGINS"
PLUGIN_FANCY_NAME = "Plugins Manager"
PLUGIN_CLASS = "PLUGINS"
PLUGIN_SORT_ORDER = 1000

class PluginManager:
    
    def getPluginsContainer(self) -> remi.gui.Container:
        """Container with list of plugins and on/off checkboxes"""
        container = None
        pl = self.app.pm.getAvailablePlugins()
        if pl:
            container = remi.gui.VBox(style={'width': '100%', 'text-align': 'center', 'align-items':'left'})
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
                self.app.registerPlugin(widget.pluginName)
            else:
                self.app.unregisterPlugin(plugin)
                

        
pluginManager = PluginManager()
@plugins.hookimpl
    

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    pluginManager.app = app
    
@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """
    defaultConfig = {
        "ACTIVE" : ["DUMMYFRAME","REMOTE","NIGHTMODE","CLOCKS","URLLOADER"]
        }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

@plugins.hookimpl
def setRemote(app):
    return pluginManager.getPluginsContainer()

@plugins.hookimpl
def saveCfg(app) -> None:
    """called before startup
    Placeholder for plugin settings to be stored.
    Use app.saveCfg(PLUGIN_NAME, dict_with_config)
    """
    pls = app.pm.getAvailablePlugins()
    active = filter(lambda p : app.pm.is_registered(p[1]), pls)
    activeNames = list(map(lambda p : p[1].PLUGIN_NAME, active))
    app.saveCfg(PLUGIN_NAME, {"ACTIVE":activeNames})