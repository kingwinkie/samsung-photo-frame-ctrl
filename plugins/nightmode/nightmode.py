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
    

    def on_bt_nightmode_pressed(self, widget):
        """remote UI"""
        mode = self.MODE.DAY if self.getMode() == self.MODE.NIGHT else self.MODE.NIGHT
        self.setMode(mode)
        text = 'Day Mode' if self.getMode() == self.MODE.NIGHT else 'Night Mode'
        self.app.remote.secureUpdate(self.bt_nightmode.set_text(text), text=text)


    def setRemote(self):
        self.bt_nightmode = gui.Button('Night Mode', width=200, height=30,  margin='4px')
        # setting the listener for the onclick event of the button
        self.bt_nightmode.onclick.do(self.on_bt_nightmode_pressed)
        table = [("Time","Mode")]
        table.extend(self.srcTable)
        self.tab_time = gui.Table.new_from_list(table,width=300, height=100, margin='4px')
        return [self.bt_nightmode,self.tab_time]
