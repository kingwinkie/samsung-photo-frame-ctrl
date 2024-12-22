import time
from enum import Enum
WHOLE_DAY = 24*60*60
class Nightmode:
    MODE = Enum("MODE",["DAY","NIGHT"])
    timeTable : list[tuple[int, MODE]] = []
    nightBrightness : int # Nightmode brightness from settings
    lastMode : MODE = None #storage for the current mode
    lastTTMode : MODE = None #storage for the current TT mode
    _forcedMode : bool = False #Nightmode is forced via remote controller
    @property
    def forcedMode(self):
        return self._forcedMode
    
    @forcedMode.setter
    def forcedMode(self, mode : MODE):
        self._forcedMode = mode
        self.setMode(mode)

    def setMode(self, mode : MODE):    
        if mode == Nightmode.MODE.NIGHT:
            self.app.setBrightness(brightness=self.nightBrightness, color=(10,0,0))
        else:
            self.app.setBrightness(brightness=255, color=(0,0,0))
        self.app.nightmode.lastMode = mode
        self.app.setStage(self.app.Stage.RESIZE)

    @staticmethod
    def getSecOfDay(t : float = None):
        """ returns sec of the day"""
        if t == None:
            t = time.time()

        secOfDay = t%(WHOLE_DAY)
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

    def checkTTModeChange(self):
        """Checks if there was a Time Table mode change since the last call. If so clears forceMode flag."""
        mode = self.getModeFromTT()
        if self.lastTTMode and self.lastTTMode != mode:
            # TT mode has been changed. Clear forced mode.
            self.forcedMode = None
        self.lastTTMode = mode

    def getModeFromTT(self, t : float = None) -> MODE:
        """ returns mode according to time table"""
        secOfDay = self.getSecOfDay( t )
        mode = next( tt for tt in self.timeTable if tt[0]< secOfDay )[1]
        return mode
    
    def getMode(self, t : float = None) -> MODE:
        """ returns mode according to time table"""
        if self.forcedMode: return self.forcedMode #Mode has been forced by remote controller
        return self.getModeFromTT(t)
            
    def getModeStr(self, mode : MODE = None) -> str:
        """returns mode string. For calling from other plugins"""
        if not mode:
            mode = self.lastMode
        return mode.name if mode else 'DAY'
        
                                  


        
    