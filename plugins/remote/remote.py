import remi.gui as gui
import remi
import logging as LOGGER

class RemoteWeb(remi.App):
    pluginsContainer = None #container with list of plugins
    verticalContainer : gui.Container # Base continer
    pluginContainers : list[gui.Container]
    def main(self, userdata):
        """basic web page"""
        self.pluginContainers = []
        caller = userdata
        # the margin 0px auto centers the main container
        self.verticalContainer = gui.Container(width='100%', margin='0px auto', style={'display': 'block', 'overflow': 'hidden'})
        
        plugins : list[tuple[str,tuple[str,list[remi.Widget]]]]= caller.createRemote()
        for plugin in plugins:
            pluginName, pluginFancyName, pluginDescr = plugin
            self.addPluginContainer(pluginName, pluginFancyName, pluginDescr)
        
        pluginSelectionContainer = caller.getPluginsContainer()
        self.verticalContainer.append([pluginSelectionContainer])

        caller.on_init(self)
        # returning the root widget
        LOGGER.debug("RC Web started")
        return self.verticalContainer
    
    def addPluginContainer(self, pluginName , pluginFancyName, plugin):
        """adds container with one plugin"""
        pluginContainer = gui.Container(width=320, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center', 'border-color': 'gray', 'border-width': '2px', 'border-style': 'solid','margin': '4px', 'padding': '2px'})
        label = gui.Label(pluginFancyName, height=12, margin='0px', style={'color':'white','background-color':'rgb(3, 88, 200)', 'font-size':'8px', 'margin-bottom':'10px'})
        pluginContainer.append(label)
        pluginContainer.append(plugin)
        pluginContainer.pluginName = pluginName
        self.verticalContainer.append(pluginContainer)
        self.pluginContainers.append(pluginContainer)

    def removePluginContainer(self, pluginName : str):
        """removes container with one plugin"""
        # look for plugin
        for pluginContainer in self.pluginContainers:
            if hasattr(pluginContainer,"pluginName") and pluginContainer.pluginName == pluginName:
                self.verticalContainer.remove_child(pluginContainer)
        
    def secureUpdate(self, func, **kwargs):
        """Thread safe update"""
        if func:
            with self.update_lock:
                #do the update
                func(**kwargs)

    
def startWeb(address : str='localhost', port : int=8088, start_browser : bool = False, caller = None) -> remi.Server:
    """Start the server."""
    server = remi.Server(RemoteWeb,title = 'Photot Frame',  start = False, address=address, port=port, start_browser=start_browser, multiple_instance=False,userdata=(caller,))
    server.start()
    return server
    
if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    startWeb(start_browser=True)