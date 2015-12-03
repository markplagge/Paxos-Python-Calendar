import threading
import queue
import leader.Leader
import MessDef
from pCalendar import UserCal
from MessDef import NetMess as MSG
import pickle
import copy
#Global Acceptor Queue:

acceptorIn = queue.Queue()
acceptorOut = queue.Queue()



''

class Acceptor(threading.Thread):
    """represents an accecptor in Paxos. Is threaded."""
    def __init__(self, daemon = True, outQ = queue.Queue(), inQ = queue.Queue(), ldr = leader.Leader.Leader(), thisIP=None):
        super().__init__()
        self.daemon = daemon
        self.outQ = outQ
        self.inQ = inQ
        self.ldr = ldr
        self.promiseN= -1
        self.promiseV= None
        self.acceptedN=None
        self.acceptedV=None

        if thisIP is None:
            self.myIP = self.ldr.myIP
        else:
            self.myIP = thisIP

        self.learner = Learner()




    #### MESSAGE PARSING / TYPING ###
    def getMessagesOfType(self,messageType):
        mx = []
        while(self.inQ.qsize() > 0):
            mx.append(self.inQ.get())
        rv = filter(lambda x: x.messType == messageType,mx)
        mx = filter(lambda x: x.messType != messageType,mx)

        for em in mx:
            self.inQ.put(em)
        return list(rv)
    def getMessageOfType(self, messageType):
        m  = self.getMessagesOfType(messageType)
        result = None
        try:
            result = m[0]
            for em in m:
                self.inQ.put(em)
        except:
            result = None

        return result

    def countMessagesOfType(self,messageType):
        v = self.getMessagesOfType(messageType)
        ct = len(v)
        for em in v:
            self.inQ.put(em)
        return ct

    ### END MESSAGE PARSING / TYPING ###
    ##CALENDAR PICKLE SERIALIZER##
    @property
    def serializedCal(self):
        pkl = None
        try:
            assert(isinstance(self.acceptedV, UserCal.Calendar))
            pkl = pickle.dumps(self.acceptedV,protocol=pickle.HIGHEST_PROTOCOL)
        except:
            pkl = None
        return pkl

    ### MESSAGE GENERATION ###
    def newPromise(self, opmsg):
        assert(isinstance(opmsg, MSG))
        """Runs when the incomming suggested value is bigger than the current promised value"""
        #TODO: Check that I'm using the "m" part of the message properly. It's the original accepted value, right?
        pkl = self.serializedCal

        outMess = MSG(messType="PROMISE", recipient = opmsg.sender, sender = self.myIP,
                      m=opmsg.accNum, accNum=self.promiseN, accVal=pkl)

        ##send message directly to the proposer we got it from
        self.outQ.put((outMess, opmsg.sender))

    def nackPromise(self, opmsg):

        opmsg.messType="NACK"
        opmsg.recipient=opmsg.sender
        opmsg.sender = self.myIP
        self.outQ.put((opmsg,opmsg.recipient))



    def accepted(self, message):
        assert(isinstance(message, MSG))
        message.messType = "ACCEPTED"
        message.accNum = self.acceptedN
        message.recipient = message.sender
        message.sender = self.myIP
        message.accVal = self.serializedCal
        self.outQ.put((message))


    def receivePrepare(self,message):
        """
        :param message: the prepare message received from the network.
        The leader/proposer has sent a prepare message, this handles it.
        :return: none
        """
        assert(isinstance(message,MessDef.NetMess))
        #Neil pointed out that we might get repeated messages... so I've got a nice if then else chain here
        #First, we assume that the proposal id is too large then smaller. dupes should fall through?
        with message.accNum as pid:
            if(self.promiseN <= message.m ):

                self.newPromise(message)
                self.promiseN = message.m
            else:
                self.nackPromise(message)


    def receiveAccept(self,message):
        assert(isinstance(message,MessDef.NetMess))



        #TODO: Check that M is the proper value here, not message.accN or whatever
        if self.promiseN <= message.m:
            self.promiseN = message.m
            self.acceptedV = message.accVal
            self.acceptedN = self.promiseN
            self.accepted(copy.deepcopy(message)) #deep copy, so we can send the same data to the learner msg generator

    def receiveCommit(self, message):
        self.learner.update(message.accVal, self.acceptedN)
        self.outQ.put(self.learner.responseMsg(message)) #destroys the message
        ##MESSAGE IS LERN'D

    def extractMessage(self,message):
        ##Multi-part message de-serializer
        return(MessDef.dePickle(message))

    def run(self):
        cases = {
            "PREPARE":self.receivePrepare,
            "ACCEPT":self.receiveAccept,
            "COMMIT":self.receiveCommit
        }
        while(True):
            if self.inQ.qsize() > 0:
                #we have a message - let's deal with it:
                message = self.extractMessage(self.inQ.get())
                cases[message.messType](message)

class lProposal(object):
    value = None
    acceptors = None

    def __init__(self,value, firstAcceptorID):
        self.value = value
        self.acceptors = []
        self.acceptors.append(firstAcceptorID)

    def newAcceptor(self, accID):
        self.acceptors.append(accID)

    @property
    def numAcceptors(self):
        """
        Gets the number of acceptors who have agreed to this value
        :rtype: int
        """
        if isinstance(self.acceptors, list):
            return len(self.acceptors)
        return 0
    def __eq__(self, other):
        if isinstance(other, lProposal):
            return self.value == other.value
        else:
            return self.value == other



class proposalTracker(object):
    proposals = []
    quorum = 1
    def __init__(self, quorum):
        self.quorum = quorum

    def addProposal(self, value, accID):
        prop = [x for x in self.proposals if x == value]
        if prop:
            prop.newAcceptor(accID)
        else:
            self.proposals.append(lProposal(value,accID))
    def getWinner(self):
        return filter(lambda v: v.numAcceptors > self.quorum,self.proposals)
    @property
    def isWinner(self):
        return len(self.getWinner()) > 0







class Learner(object):
    """
    A basic learner class - is stored within an acceptor
    """


    value = None ## The final calendar value accepted/commited
    valueStore = None ## Keeps a log of all of the versions of the calendar
    value_id = None

    def __init__(self, persistantFN="pers.dat"):
        self.values = dict()
        self.proposals = dict()
        self.fn = persistantFN


    def update(self,val,num):

        if self.

        self.cal = val
        self.versionNum = num

    def gotAccepted(self,opMessage):


    def responseMsg(self,opMessage):
        opMessage.mesType = "RESPONSE"
        opMessage.accVal = self.cal
        opMessage.recipient = opMessage.sender
        opMessage.sender = "ACCEPTOR"
        return (opMessage,opMessage.recipient)