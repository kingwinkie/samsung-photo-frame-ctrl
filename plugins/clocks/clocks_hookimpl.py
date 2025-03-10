import plugins
import imgutils
from slideshow import SlideShow
import time
import remi.gui as gui

PLUGIN_NAME = "CLOCKS"
PLUGIN_FANCY_NAME = "Clocks"
PLUGIN_SORT_ORDER = 300
PLUGIN_CLASS = "EFFECT"
class Clocks:
    app : SlideShow = None
    shownTime : str = ""
    currentDate: str = ""  # Initialize with an empty string
    textColor : str = "#F5F5DC"
    fontSize : int = 200
    fontDesc : tuple[str, str] = None # current font name, current font path
    align : tuple[imgutils.HAlign, imgutils.VAlign]

    def getDate(self) -> str:
        return time.strftime('%Y-%m-%d')  # Format the date as needed
    def getTime(self) -> str:
        text : str = time.strftime('%X')
        return text
    def showTime(self):
        if not self.app: return
        size = self.app.frameSize
	    # Get and format the current time
        time_text: str = self.getTime()
        time_text = ':'.join(time_text.split(':')[:-1])  # Remove seconds
   	 # Get and format the current date
        date_text: str = self.getDate()
        fontPath: str = None if not self.fontDesc else self.fontDesc[1]
   	 # Draw the time
        self.app.image = imgutils.drawText(text=time_text, size=size, fontSize=self.fontSize, textColor=self.textColor, align=self.align, bgImage=self.app.image, fontPath=fontPath)
   	 # Draw the date in the upper right corner
        self.app.image = imgutils.drawText(text=date_text, size=size, fontSize=self.fontSize // 2, textColor=self.textColor, align=(imgutils.HAlign.RIGHT, imgutils.VAlign.TOP), bgImage=self.app.image, fontPath=fontPath)
        self.shownTime = time_text
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

        # align
        alignCont = gui.HBox()
        lblHAlign = gui.Label('HAlign:', style={'text-align':'Left', 'margin-right':'10px'})
        ddHAlign = gui.DropDown.new_from_list([e.name for e in imgutils.HAlign],width=80, height=20, margin='4px',style={'margin-right':'10px'})
        
        ddHAlign.onchange.do(self.on_dd_halign_change)
        lblVAlign = gui.Label('VAlign:', style={'text-align':'Left', 'margin-right':'10px'})
        ddVAlign = gui.DropDown.new_from_list([e.name for e in imgutils.VAlign],width=80, height=20, margin='4px')
        if hasattr( self, "align" ):
            ddHAlign.set_value(self.align[0].name)
            ddVAlign.set_value(self.align[1].name)
        
        ddVAlign.onchange.do(self.on_dd_valign_change)
        alignCont.append([lblHAlign,ddHAlign,lblVAlign,ddVAlign])
      
        return [sizeCont, self.lblSize, self.remote_fontSize, fontCont, alignCont]
    
    def on_dd_halign_change(self, widget, value):
        self.align = (imgutils.HAlign[value], self.align[1])
        self.app.setStage(self.app.Stage.RESIZE)

    def on_dd_valign_change(self, widget, value):
        self.align = (self.align[0], imgutils.VAlign[value])
        self.app.setStage(self.app.Stage.RESIZE)

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
    cfg = app.cfg[PLUGIN_NAME]
    clocks.fontDesc = imgutils.getFontDescByName( cfg.FONT)
    clocks.textColor = cfg.FILL
    clocks.fontSize = cfg.SIZE
    clocks.align = (imgutils.HAlign[cfg.HALIGN], imgutils.VAlign[cfg.VALIGN])
    clocks.app = app

@plugins.hookimpl
def exit(app):
    return None

@plugins.hookimpl
def imageChangeBefore(app : SlideShow) -> None:
    clocks.showTime()

@plugins.hookimpl
def do(app : SlideShow) -> None:
    now = clocks.getTime()
    if now != clocks.shownTime:
        clocks.currentDate = clocks.getDate()  # Update the current date
        app.setStage(app.Stage.RESIZE)

@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config):
    """
    defaultConfig = {
        "FILL" : "#F5F5DC",
        "FONT" : None,
        "SIZE" : 200,
        "HALIGN" : "CENTER",
        "VALIGN" : "CENTER"
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig)
    

@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""
    return clocks.setRemote()

@plugins.hookimpl
def saveCfg(app) -> None:
    """called before startup
    Placeholder for plugin settings to be stored.
    Use app.saveCfg(PLUGIN_NAME, dict_with_config)
    """
    font = clocks.fontDesc[0] if clocks.fontDesc else None
    app.saveCfg(PLUGIN_NAME, {
        "FILL": clocks.textColor, 
        "FONT": font, 
        "SIZE": clocks.fontSize,
        "HALIGN": clocks.align[0].name,
        "VALIGN": clocks.align[1].name
            })

