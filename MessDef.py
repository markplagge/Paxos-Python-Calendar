
class NetMess(object):

    def __init__(self, messType="INVALID",recipient = -1, sender = -1 ,m=0,accNum=1,accVal="Calendar goes here"):
        self.messType = messType
        self.m = m
        self.accNum = accNum
        self.accVal = accVal
        self.recipient = recipient
        self.sender = sender

    def isSenderEqual(self,other):
        assert(isinstance(other,NetMess))
        return self.sender == other.sender

    def pickleMe(self):
        return ("THIS SHOULD BE PICKLED BUT IT IS NOT")




def dePickle(netm):
    return NetMess()
def createBroadcastMessArray(messType = "INVALID", N= 1, sender = -1, m = -1, accNum = -1, accVal="cal goes here"):
	
	messArray = []
	for i in range(0,N):
		messi = NetMess(messType = messType, recipient = i, sender = sender, m = m, accNum = accNum, accVal = accVal)
		messArray.append(messi)

	return messArray