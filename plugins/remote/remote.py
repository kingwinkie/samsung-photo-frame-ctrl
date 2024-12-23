import remi.gui as gui
import remi
import logging as LOGGER
import os

class RemoteWeb(remi.App):
    uploadPath : str = None #picture upload folder
    caller = None #caller class defined in remote_hookimpl
   
    def main(self, userdata):
        self.caller = userdata
        # the margin 0px auto centers the main container
        verticalContainer = gui.Container(width='100%', margin='0px auto', style={'display': 'block', 'overflow': 'hidden'})
        subContainerFrame = gui.Container(width=320, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center', 'border-color': 'gray', 'border-width': '2px', 'border-style': 'solid','margin': '4px', 'padding': '2px'})
        
        self.lbl = gui.Label('Photo Frame started', height=30, margin='10px')
        self.bt_pause = gui.Button('Pause', width=200, height=30, margin='4px')
        self.bt_pause.onclick.do(self.caller.on_bt_pause_pressed)
        self.bt_load = gui.Button('Load', width=200, height=30, margin='4px')
        self.bt_load.onclick.do(self.caller.on_bt_load_pressed)
        self.nextLoad = gui.Progress(1, 100, width=200, height=5)
        self.delayTxt_lbl = gui.Label('Delay (s):', height=20, style={'text-align':'Left','margin-top':'10px'})
        self.delayTxt = gui.TextInput(width=60, height=20, margin='10px')
        self.delayTxt.onchange.do(self.caller.on_delayTxt_changed)
        
        self.slider_brightness_lbl = gui.Label('Brightness:', height=20, margin_top='10px', style={'text-align':'Left'})
        self.slider_brightness = gui.Slider(255, 0, 255, 15, width=200, height=10, margin='1px')
        self.slider_brightness.onchange.do(self.caller.on_brightness_changed)

        realPath = os.path.join(os.path.realpath(os.path.dirname(__file__)))
        self.uploadPath = os.path.join(realPath,"uploads")
        if not os.path.isdir(self.uploadPath):
            os.mkdir(self.uploadPath)
        self.btUploadPhotoLbl = gui.Label('Upload:', height=20, margin_top='10px', style={'text-align':'Left'})
        self.btUploadPhoto = gui.FileUploader(self.uploadPath, width=200, height=30, margin='5px',accepted_files='*.jpg')
        self.btUploadPhoto.onsuccess.do(self.fileupload_on_success)
        self.btUploadPhoto.onfailed.do(self.fileupload_on_failed)

        #subContainerLeft.append(self.bt_nightmode)
        subContainerFrame.append([self.lbl, self.bt_pause, self.bt_load, self.nextLoad, self.delayTxt_lbl,self.delayTxt,self.slider_brightness_lbl, self.slider_brightness, self.btUploadPhotoLbl, self.btUploadPhoto])
        
        #horizontalContainer.append([subContainerLeft, subContainerRight])
        verticalContainer.append([subContainerFrame])
        plugins : list[tuple[str,list[remi.Widget]]]= self.caller.createRemote()
        for pluginDescr in plugins:
            pluginName = pluginDescr[0]
            plugin = pluginDescr[1]
            if plugin:
                pluginContainer = gui.Container(width=320, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center', 'border-color': 'gray', 'border-width': '2px', 'border-style': 'solid','margin': '4px', 'padding': '2px'})
                label = gui.Label(pluginName, height=12, margin='0px', style={'color':'white','background-color':'rgb(3, 88, 200)', 'font-size':'8px', 'margin-bottom':'10px'})
                pluginContainer.append(label)
                pluginContainer.append(plugin)
                verticalContainer.append(pluginContainer)

        pluginSelection = self.caller.getPluginsContainer()
        verticalContainer.append(pluginSelection)
        
        self.caller.on_init(self)
        # returning the root widget
        return verticalContainer
    
    
    def fileupload_on_failed(self, widget, filename):
        self.lbl.set_text('Photo upload failed: ' + filename)

    def fileupload_on_success(self, widget, filename):
        self.lbl.set_text('Photo upload success: ' + filename)
        fullPath : str = os.path.join(self.uploadPath, filename)
        self.caller.fileupload_on_success(widget, fullPath, filename)
        try:
            os.remove(fullPath) # remove downloaded file
        except OSError as e:
            LOGGER.error(f"File couldn't be removed {fullPath} {e}")
            pass

    def secureUpdate(self, func, **kwargs):
        if func:
            with self.update_lock:
                #do the update
                func(**kwargs)

    
def startWeb(address : str='localhost', port : int=8088, start_browser : bool = False, caller = None) -> remi.Server:
    server = remi.Server(RemoteWeb,title = 'Photot Frame',  start = False, address=address, port=port, start_browser=start_browser, multiple_instance=False,userdata=(caller,))
    server.start()
    return server
    
if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    startWeb(start_browser=True)