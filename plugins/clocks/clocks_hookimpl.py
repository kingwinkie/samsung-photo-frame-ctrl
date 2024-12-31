import plugins
import imgutils
from slideshow import SlideShow
import os.path as osp
from PIL import Image
import time
import remi.gui as gui

PLUGIN_NAME = "CLOCKS"
PLUGIN_FANCY_NAME = "Clocks"
PLUGIN_SORT_ORDER = 300
PLUGIN_CLASS = "EFFECT"
class Clocks:
    currentImage : Image
    app : SlideShow
    shownTime : str = ""
    textColor : str = "#F5F5DC"
    fontSize : int = 200
    fontDesc : tuple[str, str] = None # current font name, current font path

    def getTime(self) -> str:
        text : str = time.strftime('%H:%M' if self.app.cfg.CLOCKS.FORMAT == "24h" else '%l:%M')
        return text
    def showTime(self):
        size = self.app.cfg.FRAME.IMG_SIZE
        text : str = self.getTime()
        fontPath : str = None if not self.fontDesc else self.fontDesc[1]
        self.app.image = imgutils.drawText(text=text, size=size, fontSize=self.fontSize, textColor=self.textColor, align=(imgutils.HAlign.CENTER, imgutils.VAlign.CENTER), bgImage=self.app.image,fontPath=fontPath)
        self.shownTime = text
    # remote UI
    def setRemote(self):
        lblColor = gui.Label('Color:', style={'text-align':'Left'})
        self.remote_colorPicker = gui.ColorPicker(default_value=self.textColor, width=200, height=20, margin='4px')
        sizeCont = gui.HBox()
        sizeCont.append([lblColor, self.remote_colorPicker])
        self.lblSize = gui.Label(f'Size: {self.fontSize} px', style={'text-align':'Left'})
        self.remote_fontSize = gui.Slider(self.fontSize, 50, 700, 10, width=200, height=10, margin='1px')
        lbl_font = gui.Label(f"Font:",style={'text-align':'Left'})
        fontDescs = imgutils.getAvailableFontsDesc()
        fontNames, _ = zip(*fontDescs)
        self.dd_font = gui.DropDown.new_from_list(fontNames,width=200, height=20, margin='4px')
        fontName : str = None if not self.fontDesc else self.fontDesc[0]
        self.dd_font.set_value(fontName)
        self.dd_font.onchange.do(self.on_dd_font_change)
        fontCont = gui.HBox()
        fontCont.append([lbl_font, self.dd_font])
        # setting the listener for the onclick event of the button
        self.remote_colorPicker.onchange.do(self.on_remote_colorPicker_changed)
        self.remote_fontSize.onchange.do(self.on_remote_fontSize_changed)
        return [sizeCont, self.lblSize, self.remote_fontSize, fontCont]
    
    def on_dd_font_change(self, widget, value):
        self.fontDesc = imgutils.getFontDescByName(value)
        self.app.setStage(self.app.Stage.RESIZE)

    def setSizeText(self):
        if hasattr(self, "lblSize"):
            self.lblSize.set_text(f'Size: {self.fontSize} px')
    
    def on_remote_colorPicker_changed(self, widget, value):
        self.textColor = value
        self.app.setStage(self.app.Stage.RESIZE)
    
    def on_remote_fontSize_changed(self, widget, value):
        self.fontSize = int(value)
        self.app.setStage(self.app.Stage.RESIZE)
        self.setSizeText()

clocks = Clocks()

@plugins.hookimpl
def startup(app):
    global clocks
    clocks.fontDesc = imgutils.getFontDescByName( app.cfg[PLUGIN_NAME].FONT)
    clocks.app = app

@plugins.hookimpl
def exit(app):
    return None

@plugins.hookimpl
def imageChangeBefore(app : SlideShow) -> None:
    clocks.currentImage=app.image
    clocks.showTime()

@plugins.hookimpl
def do(app : SlideShow) -> None:
    now = clocks.getTime()
    if now != clocks.shownTime:
        app.setStage(app.Stage.RESIZE)

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config):
    """
    defaultConfig = {
        "FORMAT" : "24h",
        "FILL" : "#F5F5DC",
        "FONT" : None
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)

@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""
    return clocks.setRemote()