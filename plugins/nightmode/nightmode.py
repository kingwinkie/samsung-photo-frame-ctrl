import time
import remi.gui as gui

from enum import Enum
WHOLE_DAY = 24*60*60
class Nightmode:
    MODE = Enum("MODE",["DAY","NIGHT"])
    timeTable : list[tuple[int, MODE]] = []
    nightBrightness : int # Nightmode brightness from settings
    currentMode : MODE = None # current mode. May be set through TT or from remote
    lastCheckTT : int = 0 # day timestamp (s) of the last check
    srcTable = []
    def setMode(self, mode : MODE):
        self.currentMode = mode
        if mode == Nightmode.MODE.NIGHT:
            self.app.setBrightness(brightness=self.nightBrightness, color=(10,0,0))
        else:
            self.app.setBrightness(brightness=255, color=(0,0,0))
        self.app.setStage(self.app.Stage.RESIZE)

    @staticmethod
    def getSecOfDay(t : float = None):
        """ returns sec of the day"""
        if t == None:
            t = time.time()

        secOfDay = int(t%(WHOLE_DAY))
        return secOfDay
    
    def createTTRow(self, ttStr : tuple[str, str]) -> tuple[int, MODE]:
        """expects tuple in format ("13:57","DAY") or ("01:02 AM","NIGHT")"""
        t : time.struct_time = None
        #convert time to nr. of seconds from 00:00
        securedt = ttStr[0]+" 1970/01/01"
        try: #first try 24h format
            t = time.strptime(securedt, "%H:%M %Y/%m/%d")
        except ValueError:
            #NOW try 12h format
            t = time.strptime(securedt, "%I:%M %p %Y/%m/%d")
        secsSinceMidnight = self.getSecOfDay(time.mktime(t))
        return int(secsSinceMidnight), self.MODE[ttStr[1].upper()]
    
    def createTT(self, tt : list[tuple[str, str]]):
        """creates internal time table for getmode"""
        self.timeTable.clear()
        for item in tt:
            ttRow = self.createTTRow(item)
            self.timeTable.append(ttRow)
        self.timeTable.sort(key=lambda x:x[0])
        lastMode = self.timeTable[-1][1]
        if self.timeTable[-1][0] != WHOLE_DAY:
            self.timeTable.append((WHOLE_DAY, lastMode))
        if self.timeTable[0][0] != 0:
            self.timeTable.insert(0,(0,lastMode))
        self.timeTable.sort(key=lambda x:x[0], reverse=True) # I need the table in reverse order for getMode

    
        
    def detectTT(self, interval : range) -> bool:
        """Checks if there is at least one record in TT in the interval."""
        if interval.start == interval.stop:
            return False #ignore
        
        def detectTTpart(pInterval : range) -> bool:
            """here interval.start is always < interval.end"""
            try:
                next( tt for tt in self.timeTable if tt[0] in pInterval )
                return True #found
            except StopIteration:
                return False #not found
        
        if interval.start < interval.stop:
            return detectTTpart(interval)
        else:
            # handle midnight issue in two parts: interval.start -> midnight then 00:00:00 - interval.end
            beforeMidnight = range(interval.start, 24*60*60)
            if detectTTpart(beforeMidnight):
                return True
            afterMidnight = range(0, interval.stop)
            return detectTTpart(afterMidnight)
            
    def checkTTModeChange(self):
        """Checks if there was a Time Table mode change since the last call. If so clears forceMode flag."""
        now = self.getSecOfDay()
        changed = self.detectTT(range(self.lastCheckTT,now))
        if changed:
            mode = self.getModeFromTT()
            self.setMode(mode)
        self.lastCheckTT = now
        

    def getModeFromTT(self, t : float = None) -> MODE:
        """ returns mode according to time table"""
        secOfDay = self.getSecOfDay( t )
        mode = next( tt for tt in self.timeTable if tt[0]< secOfDay )[1]
        return mode
    
    def getMode(self, t : float = None) -> MODE:
        """ returns current mode """
        return self.currentMode if self.currentMode else self.MODE.DAY
            
    def getModeStr(self, mode : MODE = None) -> str:
        """returns mode string. For calling from other plugins"""
        if not mode:
            mode = self.currentMode
        return mode.name if mode else 'DAY'
    

    def onBtNightModePressed(self, widget):
        """remote UI"""
        mode = self.MODE.DAY if self.getMode() == self.MODE.NIGHT else self.MODE.NIGHT
        self.setMode(mode)
        text = 'Day Mode' if self.getMode() == self.MODE.NIGHT else 'Night Mode'
        self.app.remote.secureUpdate(self.bt_nightmode.set_text(text), text=text)


    def setRemote(self):
        self.bt_nightmode = gui.Button('Night Mode', width=200, height=30,  margin='4px')
        # setting the listener for the onclick event of the button
        self.bt_nightmode.onclick.do(self.onBtNightModePressed)
        
        self.tabContainer = self.addRemoteTable()
        btTabAdd = gui.Button('Add', width=100, height=20,  margin='4px')
        btTabAdd.onclick.do(self.onBtAddClicked)
        
        return [self.bt_nightmode,self.tabContainer, btTabAdd]

    def addRemoteTable(self):
        tabContainer = gui.VBox(width=310, style={'display': 'table', 'overflow': 'auto', 'text-align': 'center','margin': '4px'})            
        titleContainer = gui.HBox(style={'display': 'table-row'})          
        laTime = gui.Label("Time", width=148, height=28, margin='0px', style={'align-content:': 'center', 'display': 'table-cell', 'background':'rgba(19, 108, 209, .6)','color': 'rgb(255, 255, 255)','border': '1px','border-style': 'solid'})
        laMode = gui.Label("Mode", width=128, height=28, margin='0px', style={'display': 'table-cell', 'background':'rgba(19, 108, 209, .6)','color': 'rgb(255, 255, 255)','border': '1px','border-style': 'solid'})
        laX = gui.Label("X", width=18, height=28, margin='0px',style={'display': 'table-cell', 'background':'rgba(19, 108, 209, .6)','color': 'rgb(255, 255, 255)','border': '1px','border-style': 'solid'})
        titleContainer.append([laTime, laMode, laX])
        tabContainer.append(titleContainer)
        for srcTime in self.srcTable:
            timeRow = self.addRemoteRow(srcTime[0],self.MODE[srcTime[1].upper()])
            tabContainer.append(timeRow)
        return tabContainer
        
    def addRemoteRow(self, srcTime : str, mode : MODE):
        rowContainer = gui.HBox(style={'display': 'table-row'})            
        tiTime = gui.TextInput(width=148, height=20, margin='1px', style={'display': 'table-cell'})
        tiTime.set_value(srcTime)
        tiTime.onchange.do(self.onChangeRemoteTab)
        tiTime.valType = "time"
        #tiTime.onchange.do(self.on_tiTime_change)
        modes = [m.name for m in self.MODE]
        ddMode = gui.DropDown.new_from_list(modes,width=128, height=20, margin='1px',style={'display': 'table-cell'})
        ddMode.set_value(mode.name)
        ddMode.valType = "mode"
        ddMode.onchange.do(self.onChangeRemoteTab)
        btX = gui.Button(text = "X", width=18, height=20, margin='1px', style={'display': 'table-cell'})
        btX.onclick.do(self.onBtXClicked)
        rowContainer.append([tiTime,ddMode, btX])
        btX.rowContainer = rowContainer
        return rowContainer

    def onChangeRemoteTab(self, widget, value):
        self.rebuildSrcTab()

    def onBtXClicked(self, widget):
        rowContainer : gui.Container = widget.rowContainer
        self.tabContainer.remove_child(rowContainer)
        self.rebuildSrcTab()

    def onBtAddClicked(self, widget):
        rowContainer = self.addRemoteRow("00:00",self.MODE.DAY)    
        self.tabContainer.append(rowContainer)
        self.rebuildSrcTab()

    def rebuildSrcTab(self):
        self.srcTable = []
        for child in self.tabContainer.children:
            rowContainer = self.tabContainer.get_child(child)
            if rowContainer and len(rowContainer.children)>1:
                t = None
                mode = None
                for rowChild in rowContainer.children:
                    widget = rowContainer.get_child(rowChild)
                    if hasattr( widget, "valType"):
                        if widget.valType == "time":
                            t = widget.get_value()
                        elif widget.valType == "mode": 
                            mode = widget.get_value()
                if t and mode:
                    row = (t,mode)
                    self.srcTable.append(row)
        self.createTT(self.srcTable)
