import plugins
from  slideshow import SlideShow
import imgutils
import remi.gui as gui
import locale
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

    def getCounter(self) -> timedelta:
        if self.eventDt: 
            now = datetime.now()
            delta = self.eventDt - now
            return delta.seconds+delta.days*24*3600
        
    def show(self):

        seconds = self.getCounter()
        if seconds != None:
            size = self.app.cfg.FRAME.IMG_SIZE
            if seconds > 0:
                text : str = str(seconds)
            else:
                text = self.name if self.name else "End"

            fontPath : str = None if not self.fontDesc else self.fontDesc[1]
            self.app.image = imgutils.drawText(text=text, size=size, fontSize=self.fontSize, textColor=self.textColor, align=(imgutils.HAlign.CENTER, imgutils.VAlign.CENTER), bgImage=self.app.image,fontPath=fontPath)
            self.shownTime = text

    def setRemote(self):
        lblEv = gui.Label('Time:', style={'text-align':'Left'})
        self.evDt = gui.Date(default_value=self.eventDt.strftime("%Y-%m-%d"), width=200, height=20, margin='4px')
        self.evTm = gui.TextInput(single_line=True, default_value=self.eventDt.strftime("%X"), width=200, height=20, margin='4px')
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
        return [lblName,self.evName, evCont, sizeCont, self.lblSize, self.remote_fontSize, fontCont]
    
    
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
        countDown.show()
    

@plugins.hookimpl
def startup(app) -> None:
    """called after application start
    Placeholder for plugin initialisation
    """
    global countDown
    countDown = CountDown()
    countDown.app = app
    countDown.fontDesc = imgutils.getFontDescByName( app.cfg[PLUGIN_NAME].FONT)
    countDown.name = app.cfg[PLUGIN_NAME].NAME
    countDown.eventDt = parser.parse(app.cfg[PLUGIN_NAME].TIME)
    countDown.textColor = app.cfg[PLUGIN_NAME].FILL
    countDown.fontSize = app.cfg[PLUGIN_NAME].FONTSIZE
    
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
        "FONTSIZE" : 200,
        "TIME" : (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "NAME" : "End"
    }
    app.loadCfg(PLUGIN_NAME, defaultConfig) #load the real config and merge it with default values

@plugins.hookimpl
def do(app) -> None:
    """called every second when frame is waiting to next frame.
    Intended for showing real time etc.
    """
    # Must be shown every second
    app.setStage(app.Stage.RESIZE)



@plugins.hookimpl
def setRemote(app):
    """For setting web based remote from plugins. Returns list of remi.Widgets"""
    return countDown.setRemote()

