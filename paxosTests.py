import unittest
import paxos.Acceptor
import MessDef
import queue
import copy
import numpy
import numpy as np
class FakeServer(object):
    def __init__(self, fakeClients):
        self._inQs = {}
        self._outQs = {}
        self.clients = fakeClients
        for client in fakeClients:
            self._inQs[client] = queue.Queue()
            self._outQs[client] = queue.Queue()

        self.ct = 0
        self.max = len(self.inQs)

    @property
    def inQs(self):
        return self._inQs
    @property
    def outQs(self):
        return self._outQs

    def inQ(self,client):
        return self.inQs[client]
    def outQ(self,client):
        return self.outQs[client]


    def doServerRun(self):
        crem = self.clients[self.ct]
        outq = self.outQ(crem)
        inq = self.inQ(crem)

        assert(isinstance(outq,queue.Queue))
        if outq.qsize() > 0:
            om = outq.get()
            if isinstance(om, tuple):
                m = om[0]
                d = om[1]
                self.outQ(d).put(m)
            else:
                for s in self.outQs:
                    s.put(copy.deepcopy(om))
        self.ct +=1






class TestAcceptor(unittest.TestCase):
    def pauseWork(self):
        for acid in self.acceptors:

            acceptor = self.acceptors[acid]
            while acceptor.inQ.qsize() > 0 or  acceptor.inQ.unfinished_tasks > 0:
                pass
    def endWork(self):
        for acid in self.acceptors:

            acceptor = self.acceptors[acid]
            while acceptor.inQ.qsize() > 0 or  acceptor.inQ.unfinished_tasks > 0:
                pass
            acceptor.running  = False
    def wrd(self):
        import datetime
        from numpy import random as random

        return datetime.datetime(random.randint(1970, 2014),
                                 random.randint(1, 10),
                                 random.randint(1, 20))
    def getRvrs(self):
        def idp():
            s =  str(numpy.random.randint(1,192,1)[0])
            return s
        def ipa(x):
            return idp() + "." + idp() + "." + idp() + "." + idp()
        return list(map(ipa,range(0,self.numAcceptors)))
    def setUp(self):
        import datetime
        from numpy import random as random
        import itertools
        from pCalendar.UserCal import CalEvent,Calendar

        self.numAcceptors = 2
        numAcceptors = self.numAcceptors


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
        self.calendars = []
        for i in range(1,10):
            cal = Calendar(str(i))
            np.random.shuffle( self.events)
            cal.cal = self.events
            self.calendars.append(cal)
        ##Messages
        self.messageTypes = ["PROPOSE", "PROMISE", "ACCEPT", "COMMIT", "ACK"]


        self.recips =self.getRvrs() # [ipa() for i in range(0,numAcceptors)]
        self.senders = copy.deepcopy(self.recips)
        self.m = [1,2,3,4,5]
        self.accNums = [1,2,3,4,5]

        r = self.recips[0]
        s = self.senders[0]


        self.messages = {}
        self.messages["PREPARE"] = MessDef.NetMess(messType="PREPARE",recipient=self.recips[0],sender=self.recips[1])
        self.messages["ACCEPT"] = MessDef.NetMess(messType="ACCEPT", recipient=self.recips[0],sender=self.recips[1])
        self.messages["COMMIT"] = MessDef.NetMess(messType="COMMIT", recipient=self.recips[0],sender=self.recips[1])

        self.srvr = FakeServer(self.recips)
        self.acceptors = {}
        for client in self.recips:
            self.acceptors[client] = paxos.Acceptor.Acceptor(outQ=self.srvr.outQ(client),inQ=self.srvr.inQ(client),
                                                             thisIP=client)

#Message long
#PREPARE ->
#PROMISE <-
#ACCEPT ->
#ACK <-
#COMMIT ->

    def testPrepare(self):
        ## client 0 will send a prepare message to client 0,1. Should get a promise response:
        pm = self.messages["PREPARE"]
        pm.recipient = self.recips[1]
        pm.sender = self.senders[0]
        pm.m = 1

        for acid in self.acceptors:
            acceptor = self.acceptors[acid]
            acceptor.setDaemon(True)
            acceptor.start()
        self.srvr.inQ(self.senders[0]).put((pm,self.recips[0]))

        ##wait for acceptor to get prepare
        self.pauseWork()

        ##check that the outQ has a promise message addressed to the sender

        rm = self.srvr.outQ(self.senders[0]).get()

        dest = rm[1]
        mes = MessDef.dePickle(rm[0])
        assert(dest == self.senders[0])
        assert(mes == mes)

        ##Check that the acceptor has the right promise value:
        assert(self.acceptors[self.senders[0]].promiseN == pm.m)

        ##Test sticky

        pm.m = 0

        self.srvr.inQ(self.senders[0]).put((pm,self.recips[0]))
        rmt = self.srvr.outQ(self.senders[0]).get()

        nck = MessDef.dePickle(rmt[0])
        assert(isinstance(nck,MessDef.NetMess))
        assert(nck.messType == "NACK")
        self.endWork()


    def testAccept(self):
        import pCalendar.UserCal

        for acid in self.acceptors:
            acceptor = self.acceptors[acid]
            acceptor.setDaemon(True)
            acceptor.start()

        iq = self.srvr.inQ(self.senders[0])
        oq = self.srvr.outQ(self.senders[0])
        acc1 = self.acceptors[self.senders[0]]

        pm = self.messages["PREPARE"]
        pm.recipient = self.recips[0]
        pm.sender = self.senders[1]
        pm.m = 1

        iq.put(pm)
        self.pauseWork()
        response = oq.get()

        am = self.messages["ACCEPT"]
        am.recipient = self.recips[1]
        assert (isinstance(am,MessDef.NetMess))
        am.accNum = 1
        am.accVal = self.calendars[0]

        iq.put(am)
        self.pauseWork()
        print("Accept messages sent")
        response= MessDef.dePickle(oq.get())
        assert(isinstance(response,MessDef.NetMess))
        assert(response.messType == "ACCEPTED")
        assert(isinstance(response.accVal,pCalendar.UserCal.Calendar))
        assert(response.accVal == am.accVal)
        self.endWork()



if __name__ == '__main__':
    unittest.main()
