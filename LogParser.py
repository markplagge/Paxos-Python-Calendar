import numpy
import calendar
import os
import jsonpickle
import csv
import random
import Paxos
class LogE(object):
    """description of class"""
    """The idea here being that every time we view a calendar, the log file is used. No in-memory calendar."""
    fieldNames = ['uid','command', 'data']
    def __init__(self, fileName=None, fileObj=None, userID = 0):
        self.cd = csv.register_dialect("cd",delimiter=":", quoting=csv.QUOTE_MINIMAL,doublequote=True)
        if fileName == None:
            if fileObj is None:
                raise Exception("Use either a file name or a stream handle")

        self.fileObj = fileObj
        self.fn = fileName
        self.userID = userID

    def __loadLogFromStream(self):
        pass
    def __loadLogFromFile(self):
        cmds = []
        if os.path.isfile(self.fn) and os.path.getsize(self.fn) > 0:
            csv_file = csv.reader(open(self.fn, 'r'),dialect="cd")
            for line in csv_file:
                if len(line) > 0:
                    cmd = (line[0],line[1],line[2])
                    cmds.append(cmd)
              
            cmds = cmds[1:]
                


            #text = [line.rstrip('\n').rstrip('\r') for line in open(self.fn,mode='r')]
            #cmds = [jsonpickle.loads(line) for line in text]
            #cmds = numpy.loadtxt(self.fn,delimiter=' | ',unpack=True,dtype=(str,str))
            #with open(self.fn,mode='rb') as f:
            #    string = f.readline(
            #    cmds = numpy.loadtxt(f, delimiter='|',dtype=numpy.str,comments=None)
            #cmds = numpy.genfromtxt(self.fn,dtype=None,delimiter='|')
            #cmds = cmds[0]
        
            
        return cmds 
    def __loadLog(self, f = None):  
        if f is None:
            return self.__loadLogFromFile()
        else:
            self.fileObj = f
            return self.__loadLogFromStream()
       
    def __saveLogToStream(self,cmds):
        pass
    def __saveLogToFile(self,cmds):
        with open(self.fn,mode='w') as f:
            ins = []
            for item in cmds:
                ins.append([item[0],item[1],item[2]])

            
            writer = csv.writer(f,dialect='cd')
            writer.writerow(self.fieldNames)
            for row in ins:
                writer.writerow(row)

    def __saveLog(self, cmds, f = None):
        if f is None:
            self.__saveLogToFile(cmds)
        else:
            self.fileObj = f
            self.__saveLogToStream(cmds)        
            #f.writelines( jsonpickle.dumps(cmds))
            #numpy.savetxt(f,cmds,delimiter='|',fmt="%s")


    #Commands are insert, delete. Commands are stored in a string tuple for the purposes of this assignment - 
    #Tuple (actually a np.array) vals: "CMD","JSON_INDIVIDUAL_EVT".
    def generateCal(self):
        commands = {}
        cal = calendar.UserCal.Calendar(self.userID)
        cmds = self.__loadLog()
        if len(cmds) > 0:
             cals = list(set(cmds))
             dels = list(filter(lambda ex: 'delete' in ex, cals))
             adds = list(filter(lambda ex: 'append' in ex, cals))
             list(map(lambda i: cal.insertEvent(i[2]),adds))
             list(map(lambda i: cal.deleteEvent(i[2]),dels))
             return cal
             
        #return cmds
            
    def addLogEntry(self, logEntry):
        """
        Call this if you have a raw log entry to add to the log.
        Good for use with network stuff.
        Not so good to use if you need to hack any mainframes however. """
       

        #assuming logentry is a tuple, consisting of a uid, a string, and JSONEvent.
        cmds = self.__loadLog()
        cmds.append(logEntry)
        self.__saveLog(cmds)
        


    def __createLogWithCal(self,entryType, calEVT, uid):
        assert(calEVT,calendar.UserCal.CalEvent)
        js = calEVT.toJSON()
        entry = (uid,entryType, js)
        return entry

    def addAppend(self,calendarEvent, uid=random.randint(0,100)):
        entry = self.__createLogWithCal('append',calendarEvent,uid)   
        self.addLogEntry(entry)
        #For debugging:
        return uid

    def addDelete(self,calendarEvent, uid):
        entry = self.__createLogWithCal('delete',calendarEvent,uid)
        self.addLogEntry(entry)