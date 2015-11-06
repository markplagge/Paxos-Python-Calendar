import numpy as np
import jsonpickle
import json
import pickle
from collections import namedtuple
import datetime
import copy
busyT = namedtuple('busyT', ['start', 'end'])
emp = namedtuple('emp', ['firstName', 'lastName'])


## JSON ENCODE/DECODE date-time values
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj,dateTimePaxos):
            encoded_object = list(obj.timetuple())[0:6]
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object


def DateTimeDecoder(timeList):
    timeList = map(lambda i: int(i), timeList)
    return datetime.datetime(*timeList)




##Individual event class
class CalEvent(object):
    def __init__(self, eventName = "not a real eventName", startTS=datetime.datetime.now(), endTS=datetime.datetime.now(),
                 uid=-1, uRank="Nope", participants=[],
                 insertTime=datetime.datetime.now(), owner="Nobody"):
        self.eventName = eventName
        self.uRank = uRank
        self.uid = uid
        self.startTS = startTS
        self.endTS = endTS

        # self.eventRange = busyT(start=self.startTS, end=self.endTS)
        self.participants = participants
        self.insertTime = insertTime
        self.owner = owner
      
    @property
    def uName(self):
        return self.uid
    
    @property
    def eventRange(self):
        return busyT(start=self.startTS, end=self.endTS)

    def __str__(self):
        
        title = 'Event ID ' + str(self.uid) + ', Title: ' + str(self.eventName) + '\n '
        start = 'Start: ' + str(self.startTS) + ', '
        end = 'End: ' + str(self.endTS) + ', '
        owner = 'Owner: ' + str(self.owner) + ', '
        parts = 'Participants: ' + str(self.participants) +', '
        insert = 'Insert Time: ' + str(self.insertTime)
        return   title + start + end + priority + owner + parts + insert
    def clone(self):
        return copy.deepcopy(self)

    def __eq__(self, other):
        """

        :type other: CalEvent
        """
        assert isinstance(other.uName, object)
        return (isinstance(other, self.__class__)
                and self.uName == other.uName
                and self.uRank == other.uRank
                and self.eventRange == other.eventRange
                and self.participants == other.participants)
    
    def __lt__(self, other):
        if not isinstance(other,CalEvent):
            return NotImplemented
        if(self == other):
            return 0
        else:
            return self.startTS < other.startTS

    def compareAge(self, other):
        """
        :param other: the other cal entry
        :return: was this entry added before the other entry?(Is this entry newer?)
        """
        return self.insertTime - other.insertTime < datetime.timedelta(seconds=1)

    def calculateOverlap(self, othCal):
        assert isinstance(othCal, CalEvent)
        return self.eventRange.start < othCal.eventRange.end and othCal.eventRange.start < self.eventRange.end

        # mStart = max(self.eventRange.start, othCal.eventRange.start)
        #
        # mEnd = max(self.eventRange.end, othCal.eventRange.end)
        # return (mEnd - mStart)

    def willEventConflict(self, othCal):
        assert isinstance(othCal, CalEvent)
        overlap = self.calculateOverlap(othCal)
        #assert isinstance(overlap, datetime.timedelta)

        collab = False

        # for part in othCal.participants:
        #     collab = collab or int(self.uName) == int(part)

        for participant in self.participants:
            for oPart in othCal.participants:
                collab = collab or int(participant) == int(oPart)


        return (overlap and collab)


    def shouldAcquiesce(self, othCal):
        # compare and contrast the other item. Need more complex system
        assert isinstance(othCal, CalEvent)
        return (self != othCal or
                (self.willEventConflict(othCal)
                 and (self.compareRank(othCal) or othCal.compareAge(self))
                 )
                )

    def tostring(self, **kwargs):
        # return super().__str__(**kwargs)(self):

        output = ""
        for attr, value in self.__dict__.items():
            output = output + " " + str(attr) + ":" + str(value) + " "
        output += "\n"
        return output

    def default(o):
        if type(o) is datetime.date or type(o) is datetime.datetime:
            return o.isoformat()

    def toJSON(self):

        output = ""
        elements = self.__dict__
        elements["startTS"] = self.startTS
        elements["endTS"] = self.endTS
        elements["insertTime"] = self.insertTime
        return json.dumps(elements, cls=DateTimeEncoder, sort_keys=True, indent=2, separators=(',',': '))

    def fromJSON(self, text):
        result = jsonpickle.loads(text)

        result["startTS"] = DateTimeDecoder(result["startTS"])
        result["endTS"] = DateTimeDecoder(result["endTS"])
        result["insertTime"] = DateTimeDecoder(result["insertTime"])
        # bt1 = DateTimeDecoder(result["eventRange"][0])
        # bt2 = DateTimeDecoder(result["eventRange"][1])
        # result["eventRange"] = busyT(start=bt1, end=bt2)
        self.__dict__ = result
        return result




class Calendar(object):
    
    def __init__(self, username=0):
        if (username != ""):
            self.myUID = username
            self.fileName = str(self.myUID) + "_caldata"
            self.hrfn = "hum_" + str(self.myUID) + "_caldata.json"
            self.mrfn = "dat_" + str(self.myUID) + "_caldata.dat"
            self.cal = []
            self.caltxts = []


    def __eq__(self, other):
        if isinstance(other,Calendar):
            eventEq = self.cal == other.cal
            return eventEq
        return False

    def __str__(self, **kwargs):
        strout = "Calendar for %s:\n"+ str(self.myUID)
        strout += map(lambda evt: str(evt) + "\n", self.cal)
        return strout


    def saveCal(self):
        # pickled = []
        # for row in self.cal:
        #    pickled.append(jsonpickle.encode(row))
        # file = open(self.fileName, 'w')
        # for row in pickled:
        #    file.write(row)
        # file.close()
        self.cal.sort()
        with open(self.mrfn, 'wb') as f:
            pickle.dump(self.cal, f, pickle.HIGHEST_PROTOCOL)

        with open(self.hrfn, 'w') as f:
            self.caltxts = list(self.cal)
            btext = map(lambda i: i.toJSON(), self.caltxts)
            self.caltxts = list(btext)
            bigDict = dict(self.__dict__)
            del (bigDict["cal"])

            js1 = json.dumps(bigDict, indent=4, sort_keys=True)
            f.writelines(js1)
            # print("JS1 ---------- \n" + js1 + "\n----------------------")
        return js1

    def loadCal(self):
        # file = open(self.fileName, 'r')
        # fdat = file.readlines()
        # print(fdat)
        # self.caltxts = np.loadtxt(self.filename,delimiter=",",dtype=str)
        # file.close()
        # self.cal = []
        # for row in fdat:
        #    self.cal.append(jsonpickle.decode(row))

        with open(self.mrfn, 'rb') as ctf:
            self = pickle.load(ctf)

        jsLoaded = createCal(fileName=self.hrfn)
        assert (self == jsLoaded)
        self = jsLoaded

    def addEntry(self, calevt):
        isOverlap = False
        overlaps = []

        #CONFLICT RESOLUTION
        for event in self.cal:
            if (event.willEventConflict(calevt)):
                isOverlap = True
                overlaps.append(event)

        #         if (event.shouldAcquiesce(calevt)):
        #             acqs.append(event)
        # if (len(acqs) == len(overlaps)) and overlap == True:
        #     print('overlap uh oh OH NO NO NO NO up')
        #     # I know this is slow, but it is easier to understand
        #     for removes in overlaps:
        #         self.cal.remove(removes)
        #     self.cal.append(calevt)

        print('found %i conflicts'%len(overlaps))
        self.cal.append(calevt)
        return isOverlap, overlaps

    def removeEntry(self, calevt):
        x = "NotRemoved"
        if calevt in self.cal:
            x = self.cal.remove(calevt)
        # self.saveCal()
        return x

    def insertEvent(self, calevt):
        if isinstance(calevt,str):
            calevt = genCalEvt(calevt)
        result = self.addEntry(calevt)
        self.saveCal()
        return result

    def deleteEvent(self, calevt):
        if isinstance(calevt,str):
            calevt = genCalEvt(calevt)
        result = self.removeEntry(calevt)
        self.saveCal()
        return result

    def hasEvent(self,evt):
        return (evt in self.cal)

    def toJSON(self):
        self.saveCal()

##FILE GENERATION:
#########FACTORY FOR FILE/IO #####
# Factory Pattern for init from JSON or File:
# Note: Actual class may not include any factory pattern.

class CalGenerator(object):
    def __init__(self, source="FILE", type="JSON", fileName="", stream="", uuid=""):
        self.source = source
        self.fileName = fileName
        self.stream = stream
        self.type = type
        self.uuid = uuid
        if uuid is not "":
            tmpc = Calendar(uuid)
            if type is "JSON":
                self.fileName = tmpc.hrfn
            else:
                self.fileName = tmpc.mrfn

    def getGen(self):
        if self.type is "JSON":
            return self.initFromJSON

    def initFromJSON(self, jsSrc):
        if self.source is "FILE":
            self.ldd = jsonpickle.loads(jsSrc.read())
        if self.source is "NETWORK":
            self.ldd = jsonpickle.loads(jsSrc)
        self.newCal = Calendar(self.ldd["myUID"])
        evtList = list(map(lambda cvt: genCalEvt(cvt), self.ldd["caltxts"]))
        for evt in evtList:
            self.newCal.addEntry(evt)
        return self.newCal

    def initFromBin(self):
        self.newCal = Calendar("EMPTY")
        self.newCal.fileName = self.fileName
        self.newCal.loadCal()
        return self.newCal

    def initCalFromFile(self):
        if self.type is "JSON":
            with open(self.fileName, 'r') as jsfile:
                self.initFromJSON(jsfile)
        else:
            if self.source is "FILE":
                self.initFromBin()
        return self.newCal
