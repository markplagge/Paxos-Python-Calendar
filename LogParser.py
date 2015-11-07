import numpy
import calendar
import os
import jsonpickle
class LogE(object):
    """description of class"""
    """The idea here being that every time we view a calendar, the log file is used. No in-memory calendar."""

    def __init__(self, fileName="noFile.txt", userID = 0):
        self.fn = fileName
        self.userID = userID


    def __loadLog(self):
        cmds = []
        if os.path.isfile(self.fn):
            
            text = [line.rstrip('\n').rstrip('\r') for line in open(self.fn,mode='r')]
            cmds = [jsonpickle.loads(line) for line in text]
            #cmds = numpy.loadtxt(self.fn,delimiter=' | ',unpack=True,dtype=(str,str))
            #with open(self.fn,mode='rb') as f:
            #    string = f.readline(
            #    cmds = numpy.loadtxt(f, delimiter='|',dtype=numpy.str,comments=None)
            #cmds = numpy.genfromtxt(self.fn,dtype=None,delimiter='|')
        
            
        return cmds  
    
    def __saveLog(self, cmds):
        
        with open(self.fn,mode='w') as f:
            f.writelines( jsonpickle.dumps(cmds))
            #numpy.savetxt(f,cmds,delimiter='|',fmt="%s")


    #Commands are insert, delete. Commands are stored in a string tuple for the purposes of this assignment - 
    #Tuple (actually a np.array) vals: "CMD","JSON_INDIVIDUAL_EVT".
    def generateCal(self):
        commands = {}
        cal = calendar.UserCal.Calendar(self.userID)
        cmds = self.__loadLog()
        if len(cmds) > 0:
             cals = set(cmds)
             dels = list(filter(lambda ex: ex[0] is 'delete', cals))
             adds = list(filter(lambda ex: ex[0] is 'append',cals))
             map(lambda i: cal.insertEvent(i[1]),adds)
             map(lambda i: cal.deleteEvent(i[1]),dels)

            
    def addLogEntry(self, logEntry):
        """
        Call this if you have a raw log entry to add to the log.
        Good for use with network stuff.
        Not so good to use if you need to hack any mainframes however. """
       

        #assuming logentry is a tuple, consisting of a string and JSONEvent.
        cmds = self.__loadLog()
        
        cmds.append(logEntry)

        self.__saveLog(cmds)
        


    def __createLogWithCal(self,entryType, calEVT):
        assert(calEVT,calendar.UserCal.CalEvent)
        js = calEVT.toJSON()
        entry = (entryType, js)
        return entry

    def addAppend(self,calendarEvent):
        entry = self.__createLogWithCal('append',calendarEvent)   
        self.addLogEntry(entry)

    def addDelete(self,calendarEvent):
        entry = self.__createLogWithCal('delete',calendarEvent)
        self.addLogEntry(entry)