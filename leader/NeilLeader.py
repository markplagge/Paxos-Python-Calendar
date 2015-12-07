import threading
import queue
from leader.NeilLeaderMessDef import LeadMess
import time
import pickle

class Representative(threading.Thread):


    def __init__(self, pid=1, N=1,outQ = queue.Queue(), inQ = queue.Queue(), otherPIDs = [], otherIPs = [], curLeaderIP='127.0.0.1', myIP='127.0.0.1',timeout=5):
        super().__init__()
        self.pid = pid
        self.N = N
        self.clIP = otherIPs[N-1]
        self.myIP = myIP
        self.iAmLeader = False
        self.timeout = timeout
        self.inQ = inQ
        self.outQ = outQ
        self.otherPIDs = otherPIDs
        self.otherIPs = otherIPs
        self.runningElectionAlready = False
        self.gotOK = False
        self.gotLeader = False



        nhty = []
        for i in range(self.pid+1,self.N):
            nhty.append(i)

        self.nodesHigherThanMe = nhty



    def run(self):
        while True:
            if self.countMessagesOfType('LEADER') > 0:
                self.gotLeader = True
                leaderMessages = self.getMessagesOfType('LEADER')

                theLeaderMess = leaderMessages[0]

                self.curLeaderIP = theLeaderMess.senderIP
                trash = self.getMessagesOfType('OK')
                trash = self.getMessagesOfType('ELECTION')
                self.runningElectionAlready = False

            if self.runningElectionAlready == False:
                if self.countMessagesOfType('ELECTION') > 0:
                    #YOU RECIEVED AN ELECTION MESSAGE

                    #reply OK to him

                    electMessages = self.getMessagesOfType('ELECTION')

                    for mess in electMessages:
                        senderOfElect = mess.senderIP

                        okayMess = LeadMess('OK',self.myIP,senderOfElect)
                        pickledMess = okayMess.pickleMe()

                        self.outQ.put((pickledMess,senderOfElect))

                    if self.pid < self.N:
                        self.election()
                    # else:
                        # #I AM THE LEADER BY DEFAULT BEING THE HIGHEST NUMBER NODE
                        # self.iAmLeader = True
                        # for i in range(0,self.N):
                        #     if i != self.pid:
                        #         leaderMess = LeadMess('LEADER',self.myIP,self.otherIPs[i],senderID=self.pid)
                        #         pickledMess = leaderMess.pickleMe()
                        #
                        #         self.outQ.put((pickledMess,self.otherIPs[i]))

                #
                # if self.countMessagesOfType('LEADER') > 0:
                #     self.gotLeader = True
                #     leaderMessages = self.getMessagesOfType('LEADER')
                #
                #     theLeaderMess = leaderMessages[0]
                #
                #     self.curLeaderIP = theLeaderMess.senderIP
                #     trash = self.getMessagesOfType('OK')
                #     trash = self.getMessagesOfType('ELECTION')







    def election(self):
        self.runningElectionAlready = True
        #I need to send an elect message to all nodes above me
        for superiorNodePID in self.nodesHigherThanMe:
            electMess = LeadMess('ELECTION',self.myIP,self.otherIPs[superiorNodePID])
            pickledMess = electMess.pickleMe()

            self.outQ.put((pickledMess,self.otherIPs[superiorNodePID]))

        #WAIT FOR OKAY FROM THEM
        time.sleep(self.timeout)

        #CHECK FOR OKAY

        if self.countMessagesOfType('OK') > 0:
            okayMessages = self.getMessagesOfType('OK')
            trash = self.getMessagesOfType('ELECTION')
            self.runningElectionAlready = False
            self.gotOK = True
            return
        else:
            self.iAmLeader = True
            #YOU ARE THE LEADER
            for i in range(0,self.N):
                if i != self.pid:
                    leaderMess = LeadMess('LEADER',self.myIP,self.otherIPs[i],senderID=self.pid)
                    pickledMess = leaderMess.pickleMe()

                    self.outQ.put((pickledMess,self.otherIPs[i]))

            trash = self.getMessagesOfType('ELECTION')
            self.runningElectionAlready = False

            return





    #The worst variable names ever
    def getMessagesOfType(self,messageType):
        mx = []
        while(self.inQ.qsize() > 0):
            theMess = self.inQ.get()
            if isinstance(theMess,bytes):
                theMess = pickle.loads(theMess)
                # print(theMess)
            mx.append(theMess)
        rv = filter(lambda x: x.messType == messageType,mx)
        mx = filter(lambda x: x.messType != messageType,mx)

        for em in mx:
            self.inQ.put(em)
        return list(rv)


    def countMessagesOfType(self,messageType):
        v = self.getMessagesOfType(messageType)
        ct = len(v)
        for em in v:
            self.inQ.put(em)
        return ct

