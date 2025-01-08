import plugins
from  slideshow import SlideShow
import imgutils
import remi.gui as gui
from enum import Enum
import math
PLUGIN_NAME = "COUNTDOWN" # set plugin name here. This must be the same as prefix of this file.
PLUGIN_FANCY_NAME = "Count Down" # set fancy name for remote controller here
PLUGIN_CLASS = "EFFECT" # Classes are: LOADER (force load after change), DISPLAY (at least one must stay active), REMOTE(can't be unloaded from web)
PLUGIN_SORT_ORDER = 320 #Order for remote controller dialogs. Ascending.
from datetime import datetime, timedelta
from dateutil import parser
class CountDown:
    eventDt : datetime = None
    app : SlideShow = None
    name : str = "End"
    textColor : str = "#F5F5DC"
    fontSize : int = 200
    fontDesc : tuple[str, str] = None # current font name, current font path
    lastText : str = None # last text shown
    align : tuple[imgutils.HAlign, imgutils.VAlign]
    class Format(Enum):
        SECONDS = "SECONDS"
        DAYS_SECONDS = "DAYS_SECONDS"
        DAYS_HOURS_SECONDS = "DAYS_HOURS_SECONDS"
        DAYS_HOURS_MINUTES_SECONDS = "DAYS_HOURS_MINUTES_SECONDS"
        @classmethod
        def getName(cls, value):
            if value == cls.SECONDS:
                return "Seconds"
            elif value == cls.DAYS_SECONDS:
                return "Days, Seconds"
            elif value == cls.DAYS_HOURS_SECONDS:
                return "Days, Hours, Seconds"
            elif value == cls.DAYS_HOURS_MINUTES_SECONDS:
                return "Days, Hours, Minutes, Seconds"
            else:
                return "Unknown"
        @classmethod
        def setByName(cls, name):
            if name == "Seconds":
                return cls.SECONDS
            elif name == "Days, Seconds":
                return cls.DAYS_SECONDS
            elif name == "Days, Hours, Seconds":
                return cls.DAYS_HOURS_SECONDS
            elif name == "Days, Hours, Minutes, Seconds":
                return cls.DAYS_HOURS_MINUTES_SECONDS
            
    format : Format = Format.SECONDS

    def getCounter(self) -> timedelta:
        if self.eventDt: 
            now = datetime.now()
            delta = self.eventDt - now
            return delta.seconds+delta.days*24*3600
        

    def getText(self):
        seconds = self.getCounter()
        text : str = None
        num : int = seconds
        if seconds != None:
            if seconds > 0:
                if self.format == self.Format.DAYS_HOURS_MINUTES_SECONDS:
                    if seconds > 24*3600:
                        num = seconds / (24*3600)
                    elif seconds > 3600:
                        num = seconds / (3600)
                    elif seconds > 60:
                        num = seconds / 60
                elif self.format == self.Format.DAYS_HOURS_SECONDS:
                    if seconds > 24*3600:
                        num = seconds / (24*3600)
                    elif seconds > 3600:
                        num = seconds / (3600)
                elif self.format == self.Format.DAYS_SECONDS:
                    if seconds > 24*3600:
                        num = seconds / (24*3600)
                text = str(math.floor(num))
            else:
                text = self.name if self.name else "End"
        return text

    def show(self, text : str):
        if text:    
            # text size
            fontPath : str = None if not self.fontDesc else self.fontDesc[1]
            font = imgutils.createFont( fontSize=self.fontSize, fontPath=fontPath)
            # calculate more stable testSize
            textForSize = "".ljust(len(text),"8")
            textSize = imgutils.getTextSize(textForSize, font)
            self.app.image = imgutils.drawText(text=text, size=self.app.frameSize, fontSize=self.fontSize, textColor=self.textColor, align=self.align, bgImage=self.app.image, fontPath=fontPath, textSize=textSize)
            self.shownTime = text

    def setRemote(self):
        lblEv = gui.Label('Time:', style={'text-align':'Left'})
        self.evDt = gui.Date(default_value=self.eventDt.strftime("%Y-%m-%d"), width=120, height=20, margin='4px')
        self.evTm = gui.TextInput(single_line=True, default_value=self.eventDt.strftime("%X"), width=80, height=20, margin='4px')
        self.evTm.set_value(self.eventDt.strftime("%H:%M:%S"))
        self.evDt.onchange.do(self.on_ev_change_dt)
        self.evTm.onchange.do(self.on_ev_change_dt)
        lblName = gui.Label('Name:', style={'text-align':'Left'})
        self.evName = gui.TextInput(single_line=True, width=200, height=20, margin='4px')
        self.evName.set_value(self.name)
        self.evName.onchange.do(self.on_ev_name_change)
        
        evCont = gui.HBox()
        evCont.append([lblEv, self.evDt, self.evTm])

        lblColor = gui.Label('Color:', style={'text-align':'Left'})
        self.remote_colorPicker = gui.ColorPicker(default_value=self.textColor, width=200, height=20, margin='4px')
        sizeCont = gui.HBox()
        sizeCont.append([lblColor, self.remote_colorPicker])
        
        # align
        alignCont = gui.HBox()
        lblHAlign = gui.Label('HAlign:', style={'text-align':'Left', 'margin-right':'10px'})
        ddHAlign = gui.DropDown.new_from_list([e.name for e in imgutils.HAlign],width=80, height=20, margin='4px',style={'margin-right':'10px'})
        ddHAlign.set_value(self.align[0].name)
        ddHAlign.onchange.do(self.on_dd_halign_change)
        lblVAlign = gui.Label('VAlign:', style={'text-align':'Left', 'margin-right':'10px'})
        ddVAlign = gui.DropDown.new_from_list([e.name for e in imgutils.VAlign],width=80, height=20, margin='4px')
        ddVAlign.set_value(self.align[1].name)
        ddVAlign.onchange.do(self.on_dd_valign_change)
        alignCont.append([lblHAlign,ddHAlign,lblVAlign,ddVAlign])
        
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

        formatCont = gui.HBox()
        formats = list(map(lambda x: self.Format.getName(x),self.Format))
        lbl_format  = gui.Label("Format:",style={'text-align':'Left'})
        dd_format = gui.DropDown.new_from_list(formats,width=200, height=20, margin='4px')
        dd_format.set_value(self.format.getName(self.format))
        dd_format.onchange.do(self.on_dd_format_change)
        formatCont.append([lbl_format, dd_format])

        
        return [lblName,self.evName, evCont, sizeCont, self.lblSize, self.remote_fontSize, fontCont,formatCont, alignCont]
    
    def on_dd_format_change(self, widget, value):
        self.format = self.Format.setByName(value)
    
    def on_ev_name_change(self, widget, value):
        self.name = value
    
    def on_ev_change_dt(self, widget, value):
        t = parser.parse(self.evTm.get_value())
        d = datetime.strptime(self.evDt.get_value(), "%Y-%m-%d") 
        self.eventDt= datetime.combine(d.date(), t.time())
        self.app.setStage(self.app.Stage.RESIZE)


    def on_dd_font_change(self, widget, value):
        self.fontDesc = imgutils.getFontDescByName(value)
        self.app.setStage(self.app.Stage.RESIZE)

    def on_dd_halign_change(self, widget, value):
        self.align = (imgutils.HAlign[value], self.align[1])
        self.app.setStage(self.app.Stage.RESIZE)

    def on_dd_valign_change(self, widget, value):
        self.align = (self.align[0], imgutils.VAlign[value])
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

countDown : CountDown = None

@plugins.hookimpl
def exit(app) -> None:
    """called when application is about to quit
    Placeholder for plugin cleanup
    """
    

@plugins.hookimpl
def imageChangeBefore(app) -> None:
    """called before image was changed on the screen
    Intended for effects etc. Image is in app.image
    """
    if countDown:
        countDown.show(countDown.getText())
    
@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    global countDown
    countDown = CountDown()
    countDown.app = app
    cfg = app.cfg[PLUGIN_NAME]
    countDown.fontDesc = imgutils.getFontDescByName( cfg.FONT)
    countDown.name = cfg.NAME
    countDown.eventDt = parser.parse(cfg.TIME)
    countDown.textColor = cfg.FILL
    countDown.fontSize = cfg.SIZE
    if cfg.FORMAT:
        countDown.format = CountDown.Format[cfg.FORMAT]
    else:
        countDown.format = CountDown.Format.SECONDS
    countDown.align = (imgutils.HAlign[cfg.HALIGN], imgutils.VAlign[cfg.VALIGN])
    
@plugins.hookimpl
def loadCfg(app) -> None:
    """called before startup
    Placeholder for plugin default settings
    Use app.loadCfg(PLUGIN_NAME, dict_with_config)
    """

    defaultConfig = {
        "FORMAT" : "24h",
        "FILL" : "#F5F5DC",
        "FONT" : None,
        "SIZE" : 200,
        "TIME" : (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "NAME" : "End",
        "FORMAT" : "SECONDS",
        "HALIGN" : "CENTER",
        "VALIGN" : "CENTER"
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

@plugins.hookimpl
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """
    if countDown:
        newText = countDown.getText()
        if  newText != countDown.lastText:
            app.setStage(app.Stage.RESIZE) # force repaint
            countDown.lastText = newText

@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""
    return countDown.setRemote()

@plugins.hookimpl
def saveCfg(app) -> None:
    """called before startup
    Placeholder for plugin settings to be stored.
    Use app.saveCfg(PLUGIN_NAME, dict_with_config)
    """
    font = countDown.fontDesc[0] if countDown.fontDesc else None
    app.saveCfg(PLUGIN_NAME, 
        {"FILL": countDown.textColor,
            "FONT": font, 
            "SIZE": countDown.fontSize, 
            "TIME": countDown.eventDt.strftime("%Y-%m-%d %H:%M:%S"), 
            "NAME": countDown.name,
            "FORMAT": countDown.format.name,
            "HALIGN": countDown.align[0].name,
            "VALIGN": countDown.align[1].name
        }) 