import threading
import queue

import leader.Leader
import MessDef
from pCalendar import UserCal
from MessDef import NetMess as MSG
import pickle
import copy
import numpy as np
import unittest


import os
import unittest
#Global Acceptor Queue:

acceptorIn = queue.Queue()
acceptorOut = queue.Queue()



''

class Acceptor(threading.Thread):
    """represents an accecptor in paxos. Is threaded."""
    def __init__(self, daemon = True, outQ = queue.Queue(), inQ = queue.Queue(), ldr = None, thisIP="127.0.0.1", thisPort="5309"):
        super().__init__()
        self.running = True
        self.daemon = daemon
        self.outQ = outQ
        self.inQ = inQ
        self.ldr = ldr
        self.promiseN= -1
        self.promiseV= None
        self.acceptedN=None
        self.acceptedV=None
        self.ldr = ldr
        if ldr is None:
            self.myIP =  thisIP
        else:
            try:
                assert(isinstance(ldr,leader.Leader.Leader) or
                       isinstance(ldr,leader.Leader.LeaderAs))
                self.myIP = self.ldr.myIP
            except:
                print("Acceptor error - no valid leader given, or no IP set.")
                print("My IP is " + str(self.myIP) + ", LDR is " + str(ldr))
                exit(-1)

        self.learner = Learner(thisIP+thisPort)




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
        # pkl = None
        # try:
        #     assert(isinstance(self.acceptedV, UserCal.Calendar))
        #     pkl = pickle.dumps(self.acceptedV,protocol=pickle.HIGHEST_PROTOCOL)
        # except:
        #     pkl = None
        # return pkl
        return self.promiseV

    ### MESSAGE GENERATION ###
    def newPromise(self, opmsg):
        assert(isinstance(opmsg, MSG))
        """Runs when the incomming suggested value is bigger than the current promised value"""
        #TODO: Check that I'm using the "m" part of the message properly. It's the original accepted value, right?
        pkl = self.serializedCal

        outMess = MSG(messType="PROMISE", recipient = opmsg.sender, sender = self.myIP,
                      m=opmsg.accNum, accNum=self.promiseN, accVal=pkl)

        print("Acceptor: Sending Promise(%i, %s)"%(self.promiseN,type(pkl)))

        ##send message directly to the proposer we got it from
        self.outQ.put((outMess.pickleMe(), opmsg.sender))

    def nackPromise(self, opmsg):

        opmsg.messType="NACK"
        opmsg.recipient=opmsg.sender
        opmsg.sender = self.myIP
        self.outQ.put((opmsg.pickleMe(),opmsg.recipient))



    def accepted(self, message):
        assert(isinstance(message, MSG))
        message.messType = "ACK"
        message.accNum = self.acceptedN
        message.recipient = message.sender
        message.sender = self.myIP
        message.accVal = self.acceptedV

        print("Acceptor: Sending Ack(%i %s)"%(message.accNum, type(message.accVal)))
        self.outQ.put(message.pickleMe())


    def receivePrepare(self,message):
        """
        :param message: the prepare message received from the network.
        The leader/proposer has sent a prepare message, this handles it.
        :return: none
        """
        assert(isinstance(message,MessDef.NetMess))
        #Neil pointed out that we might get repeated messages... so I've got a nice if then else chain here
        #First, we assume that the proposal id is too large then smaller. dupes should fall through?
        m = int(message.m)

        if(self.promiseN <= m ):
            self.promiseN = m
            self.newPromise(message)
        else:
            self.nackPromise(message)


    def receiveAccept(self,message):
        assert(isinstance(message,MessDef.NetMess))



        #TODO: Check that M is the proper value here, not message.accN or whatever
        if self.promiseN <= message.m:
            # self.promiseN = message.accVal #What was the point of this....
            self.acceptedV = message.accVal
            self.promiseN = message.m

            self.acceptedN = self.promiseN
            self.accepted(copy.deepcopy(message)) #deep copy, so we can send the same data to the learner msg generator

    def receiveCommit(self, message):
        response = self.learner.gotCommit(message)

        #self.learner.update(message.accVal, self.acceptedN)
        # self.outQ.put((response[0].pickleMe(),response[1])) #destroys the message
        ##MESSAGE IS LERN'D

    def extractMessage(self,message):
        return message
        ##Multi-part message de-serializer
        #return(MessDef.dePickle(message))


    def run(self):

        cases = {
            "PREPARE":self.receivePrepare,
            "ACCEPT":self.receiveAccept,
            "COMMIT":self.receiveCommit
        }
        while(self.running):
            if self.inQ.qsize() > 0:
                #we have a message - let's deal with it:
                message = self.extractMessage(self.inQ.get())
                if isinstance(message,tuple):
                    message = message[0]
                cases[message.messType](message)
                self.inQ.task_done()


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
    def checkAddProposal(self,value,accID):
        if(self.isWinner):
            return True
        self.addProposal(value,accID)
        return self.isWinner



    def addProposal(self, value, accID):
        prop = [x for x in self.proposals if x == value]
        if len(prop) > 0:
            prop[0].newAcceptor(accID)
        else:
            self.proposals.append(lProposal(value,accID))
    def getWinner(self):
        return list(filter(lambda v: v.numAcceptors > self.quorum,self.proposals))
    @property
    def isWinner(self):
        return len(self.getWinner()) > 0







class Learner(object):
    """
    A basic learner class - is stored within an acceptor
    """


    value = None ## The final calendar value accepted/commited
    valueStore = []## Keeps a log of all of the versions of the calendar
    value_id = None

    def __init__(self,pid, persistantFN="Pstorage.dat"):
        self.values = []
        self.pid = pid
        self.fn = str(pid) + persistantFN
        self.ccal = None
        self.ccalVersion = None

        if os.path.isfile(self.fn):
            with open(self.fn, mode="rb") as file:
                self.values = pickle.load(file)
                self.ccal = self.values[0][1]
                self.ccalVersion = self.values[0][0]








    def getAll(self):
        return self.values

    @property
    def currentCal(self):
        return self.ccal


    def update(self,val,num):
        self.ccal = val
        self.ccalVersion = num
        self.values.append((num,val))
        with open(self.fn, mode="wb") as file:
            pickle.dump(self.values, file,protocol=pickle.HIGHEST_PROTOCOL)

        with open("human_log.log", mode="a") as file:
            for val in self.values:
                file.write("Entry - " + str(val[1]))





    def gotCommit(self, opMessage):
        self.update(opMessage.accVal,opMessage.accNum)
        return self.responseMsg(opMessage)

    def responseMsg(self,opMessage):
        opMessage.mesType = "RESPONSE"
        opMessage.accVal = self.ccal
        opMessage.accNum = self.ccalVersion
        opMessage.recipient = opMessage.sender
        opMessage.sender = "ACCEPTOR"
        return (opMessage,opMessage.recipient)

"""******************************************************************************
UNIT TESTS FOR VARIOUS THINGS
"""

class testProposal(unittest.TestCase):
    numVals = 100000
    def setUp(self):

        self.propt = proposalTracker((self.numVals / 2 )+1)

        self.pids = []
        for i in range(1,self.numVals):
            self.pids.append("[Pₓ=" + str(i) + "]")

        v=np.tile([1,2],self.numVals - 1)
        v = list(v) + [1]

        np.random.shuffle(v )
        self.vals = list( v )

        self.procValList = []
        for pid in self.pids:
            self.procValList.append((self.vals.pop(),pid))
        print(self.procValList)
        self.vals = list(v)



    def testAddChecker(self):
        tester = False
        for pvp in self.procValList:
            if self.propt.checkAddProposal(pvp[0],pvp[1]):
                tester = True
                break
        assert(tester)


    def testAddValues(self):
        #receive "commit" messages
        for pvp in self.procValList:
            self.propt.addProposal(pvp[0],pvp[1])
        assert(self.propt.isWinner)


class testLearner(unittest.TestCase):

    def wrd(self):
        import datetime
        from numpy import random as random

        return datetime.datetime(random.randint(1970, 2014),
                                 random.randint(1, 10),
                                 random.randint(1, 20))
    def tearDown(self):
        for fn in self.createdFiles:
            os.remove(fn)


    def setUp(self):
        import datetime
        from numpy import random as random
        import itertools
        from pCalendar.UserCal import CalEvent



        startDates = []
        endDates = []

        fns = ["bob", "john", "ringo", "Paul", "Conan", "Mike"]
        lns = ["Mario", "Luigi", "Walker", "LaQuarius", "Edmond", "Aadams"]
        rnks = ["pleb", "midLevel", "CEO"]

        self.events = []
        fullNames = [fns, lns]
        self.employeeList = []

        for list in itertools.product(*fullNames):
            self.employeeList.append(list)
        # going to use about 50% overlap events for test:
        startD = 1
        startE = 4
        for _ in range((int(len(self.employeeList) / 2))):
            startDates.append(datetime.datetime(2016, 1, startD,
                                                random.randint(1, 10),
                                                random.randint(1, 5),
                                                random.randint(1, 50)))
            endDates.append(datetime.datetime(2016, 1, startE,
                                              random.randint(1, 10),
                                              random.randint(1, 5),
                                              random.randint(1, 50)))
            startD += 1
            startE += 1
        for _ in range((len(self.employeeList))):
            sd = (self.wrd())
            startDates.append(sd)
            endDates.append(sd + datetime.timedelta(5))

        for i in range(len(self.employeeList)):
            self.events.append(CalEvent(startDates[i], endDates[i], self.employeeList[i][0],
                                        self.employeeList[i][1], random.choice(rnks), "NONE"))
        self.startDates = startDates
        self.endDates = endDates
        self.createdFiles = []

    def testSave(self):
        import datetime
        from numpy import random as random
        import itertools
        from pCalendar.UserCal import CalEvent,Calendar

        cald = Calendar("UnitTester")
        cald.events = self.events
        #create a fresh learner:
        learnTst = Learner("unitTest-" + str( random.randint(1,10000)))
        message = MessDef.NetMess(messType="COMMIT", recipient="127.0.0.1", accNum=1, accVal = cald)
        learnTst.gotCommit(message)
        self.createdFiles.append(learnTst.fn)
        ## check that file exists now:
        assert(os.path.isfile(learnTst.fn))
        ##OK ! saved this sucker to disk!!!

    def testLoad(self):
        import datetime
        from numpy import random as random
        import itertools
        from pCalendar.UserCal import CalEvent,Calendar
        cald = Calendar("UnitTester")
        cald.events = self.events
        #create a fresh learner:
        message = MessDef.NetMess(messType="COMMIT", recipient="127.0.0.1", accNum=1, accVal = cald)
        lrnID  = "unitTest-" + str( random.randint(1,10000))
        learnTst = Learner(lrnID)
        learnTst.gotCommit(message)

        loadLrn = Learner(lrnID)
        self.createdFiles.append(learnTst.fn)
        self.createdFiles.append(loadLrn.fn)
        print("OP is {}, learned is {}".format(cald,loadLrn.currentCal) )
        assert(cald == loadLrn.currentCal)




