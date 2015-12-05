import pCalendar
import jsonpickle
import pickle
import json
from pCalendar.UserCal import Calendar
## Calendar additions:





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
        #try:
        #    assert(isinstance(self.accVal,Calendar))
        #    #Calendar.jsonCal = self.accVal.jsonCal()
        #    self.accValTxt = pickle#self.accVal.jsonCal()
        #except AssertionError:
        #    self.accVal = None
        #    self.accValTxt = None
        #    print("PCKLR Status update - message with no value - info ok")
        #except:
        #    print("possible uk er")

        return pickle.dumps(self)

    def __eq__(self, other):
        if isinstance(other,NetMess):
            return (self.messType == other.messType and
                    self.m == other.m and
                    self.accNum == other.accNum and
                    self.accVal == other.accVal and
                    self.recipient == other.recipient and
                    self.sender == other.sender)
        else:
            return False



    




def dePickle(netm):
    """gives you a message from a decoded byte string """
    try:

        #depickle original object:
        message = pickle.loads(netm)
        assert(isinstance(message,NetMess))
        ## load the internal str and de-pickle that:
        if message.accValTxt is not None:
            # print("Textual calendar!")
            cg = pCalendar.UserCal.CalGenerator(source="NETWORK").getGen()
            message.accVal = cg(message.accValTxt)
            if(not isinstance(message.accVal,NetMess)):
                raise "Bad Cal"
        else:
            # print("binary cal")
            pass

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

