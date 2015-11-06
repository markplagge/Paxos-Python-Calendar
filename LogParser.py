import numpy
import calendar
import os

class LogE(object):
    """description of class"""
    """The idea here being that every time we view a calendar, the log file is used. No in-memory calendar."""

    def __init__(self, fileName="noFile.txt", userID = 0):
        self.fn = fileName
        self.userID = userID
    #Commands are insert, delete. Commands are stored in a string tuple for the purposes of this assignment - 
    #Tuple (actually a np.array) vals: "CMD","JSON_INDIVIDUAL_EVT".
    def generateCal(self):
         commands = {}
         cal = calendar.UserCal.Calendar(self.userID)
         if os.path.isfile(self.fn):
             with open(self.fn,mode='r') as f:
                 cmds = numpy.loadtxt(f,dtype=str)
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

        with open(self.fn,mode='r') as f:
            cmds = numpy.loadtxt(f, dtype=str,delimiter=',')

        #assuming logentry is a tuple, consisting of a string and JSONEvent.
        cmds.append(logEntry)

        with open(self.fn,mode='w') as f:
            numpy.savetxt(f,cmds,delimiter=',')


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