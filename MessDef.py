import pCalendar
import jsonpickle
import pickle
import json
from pCalendar.UserCal import Calendar
## Calendar additions:


def jsonCal(self):
    self.cal.sort()
    self.caltxts = list(self.cal)
    btext = map(lambda i: i.toJSON(), self.caltxts)
    self.caltxts = list(btext)
    bigDict = dict(self.__dict__)
    del (bigDict["cal"])

    js1 = json.dumps(bigDict, indent=4, sort_keys=True)
    return js1


class NetMess(object):

    def __init__(self, messType="INVALID",recipient = -1, sender = -1 ,m=-1,accNum=-1,accVal="Calendar goes here"):
        self.messType = messType
        self.m = m
        self.accNum = accNum
        self.accVal = accVal
        self.recipient = recipient
        self.sender = sender

        self.accValTxt = None

    def isSenderEqual(self,other):
        assert(isinstance(other,NetMess))
        return self.sender == other.sender

    def pickleMe(self):
        ## pickle the calendar
        try:
            assert(isinstance(self.accVal,Calendar))
            Calendar.jsonCal = jsonCal
            self.accValTxt = self.accVal.jsonCal()

        except AssertionError:
            self.accVal = None
            self.accValTxt = None
            print("PCKLR Status update - message with no value - info ok")
        except:
            print("possible uk er")

        return pickle.dumps(self)



    




def dePickle(netm):
    """gives you a message from a decoded byte string """
    try:

        #depickle original object:
        message = pickle.loads(netm)
        assert(isinstance(message,NetMess))
        ## load the internal str and de-pickle that:
        if message.accValTxt is not None:
            cg = pCalendar.UserCal.CalGenerator(source="NETWORK").getGen()
            message.accVal = cg(message.accValTxt)
            if(not isinstance(message.accVal,NetMess)):
                raise "Bad Cal"

        return message
    except AssertionError:
        print("Depickled message {} but it was not a NetMess. Object was ".format(netm) + str(message))
    except "Bad Cal":
        print("Error with calendar depickle")
    except:
        print("unknown error during  depickle")

    return None







def createBroadcastMessArray(messType = "INVALID", N= 1, sender = -1, m = -1, accNum = -1, accVal="cal goes here"):
	
	messArray = []
	for i in range(0,N):
		messi = NetMess(messType = messType, recipient = i, sender = sender, m = m, accNum = accNum, accVal = accVal)
		messArray.append(messi)

	return messArray

