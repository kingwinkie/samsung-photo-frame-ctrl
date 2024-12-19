import remi.gui as gui
import remi
import logging as LOGGER
import os


class RemoteWeb(remi.App):
    uploadPath : str = None #picture upload folder
    caller = None #caller class defined in remote_hookimpl
    def __init__(self, *args):
        super(RemoteWeb, self).__init__(*args)

    def main(self, userdata):
        self.caller = userdata
        global server
        server = self
        # the margin 0px auto centers the main container
        verticalContainer = gui.Container(width='100%', margin='0px auto', style={'display': 'block', 'overflow': 'hidden'})
        horizontalContainer = gui.Container(width='100%', layout_orientation=gui.Container.LAYOUT_HORIZONTAL, margin='0px', style={'display': 'block', 'overflow': 'auto'})
        subContainerLeft = gui.Container(width=320, style={'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        # the arguments are	width - height - layoutOrientationOrizontal
        subContainerRight = gui.Container(style={'width': '220px', 'display': 'block', 'overflow': 'auto', 'text-align': 'center'})
        self.lbl = gui.Label('Photo Frame started', width=200, height=30, margin='10px')
        self.bt_nightmode = gui.Button('Night Mode', width=200, height=30)
        # setting the listener for the onclick event of the button
        self.bt_nightmode.onclick.do(self.caller.on_bt_nightmode_pressed)

        self.slider_brightness_lbl = gui.Label('Brightness', width=200, height=20, margin_top='10px')
        self.slider_brightness = gui.Slider(255, 0, 255, 15, width=200, height=10, margin='1px')
        self.slider_brightness.onchange.do(self.caller.on_brightness_changed)

        self.bt_pause = gui.Button('Pause', width=200, height=30)
        self.bt_pause.onclick.do(self.caller.on_bt_pause_pressed)

        self.bt_load = gui.Button('Load', width=200, height=30)
        self.bt_load.onclick.do(self.caller.on_bt_load_pressed)
        
        self.delayTxt_lbl = gui.Label('Delay (s)', width=200, height=20, margin='10px')
        self.delayTxt = gui.TextInput(width=200, height=30, margin='10px')
        self.delayTxt.set_text('15')
        self.delayTxt.onchange.do(self.caller.on_delayTxt_changed)

        realPath = os.path.join(os.path.realpath(os.path.dirname(__file__)))
        self.uploadPath = os.path.join(realPath,"uploads")
        if not os.path.isdir(self.uploadPath):
            os.mkdir(self.uploadPath)
        self.inputUploadPhoto=gui.Input(type='file', accept='image/*', attributes={'capture': 'camera'})
        self.inputUploadPhoto.onchange.do(self.caller.on_file_upload_input)
        self.btUploadPhoto = gui.FileUploader(self.uploadPath, width=200, height=30, margin='10px',accepted_files='*.jpg')
        self.btUploadPhoto.onsuccess.do(self.fileupload_on_success)
        self.btUploadPhoto.onfailed.do(self.fileupload_on_failed)

        subContainerLeft.append([self.bt_nightmode, self.slider_brightness_lbl, self.slider_brightness, self.btUploadPhoto, self.inputUploadPhoto])
        subContainerRight.append([ self.bt_pause,self.bt_load,self.delayTxt_lbl,self.delayTxt])
        horizontalContainer.append([subContainerLeft, subContainerRight])
        verticalContainer.append([self.lbl, horizontalContainer])

        self.caller.on_init(self)
        # returning the root widget
        return verticalContainer
    
    
    def fileupload_on_failed(self, widget, filename):
        self.lbl.set_text('Photo upload failed: ' + filename)

    def fileupload_on_success(self, widget, filename):
        self.lbl.set_text('Photo upload success: ' + filename)
        fullPath : str = os.path.join(self.uploadPath, filename)
        self.caller.fileupload_on_success(widget, fullPath)
        try:
            os.remove(fullPath) # remove downloaded file
        except OSError as e:
            LOGGER.error(f"File couldn't be removed {fullPath} {e}")
            pass

    def secureUpdate(self, func, **kwargs):
        if func:
            with server.update_lock:
                #do the update
                func(**kwargs)

server : RemoteWeb = None

def nightmodeSetText(text : str):
    if server:
        server.secureUpdate(server.bt_nightmode.set_text(text), text=text)

def brightnessFB(brightness : int):
    if server:
        server.secureUpdate(server.slider_brightness.set_value( brightness ), brightness=brightness)

def delayTxtFB(delay : int):
    if server:
        server.secureUpdate(server.delayTxt.set_text( str(delay)), delay=delay)

def pausedSetText(text : str):
    if server:
        server.secureUpdate(server.bt_pause.set_text(text), text=text)

def startWeb(address : str='localhost', port : int=8088, start_browser : bool = False, caller = None):
    global global_app_instance
    server = remi.Server(RemoteWeb, start = False, address=address, port=port, start_browser=start_browser, multiple_instance=False,userdata=(caller,))
    server.start()



if __name__ == "__main__":
    # starts the webserver
    # optional parameters
    # start(MyApp,address='127.0.0.1', port=8081, multiple_instance=False,enable_file_cache=True, update_interval=0.1, start_browser=True)
    startWeb(start_browser=True)