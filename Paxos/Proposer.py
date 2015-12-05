﻿#Neil McGlohon - Nov 22, 2015

import threading
import queue
from leader.Leader import Leader
import MessDef
import math
from time import sleep

# proposerIn = queue.Queue()
# proposerOut = queue.Queue()


timeout = 5 #time to wait for queue to determine if majority has been found


class Proposer(threading.Thread):

    def __init__(self,inQ,outQ,requestInQ, clientOutQ, N= 1, ID= -1, ldr= Leader(), timeout = 5):
        """Change q references later on to outQ and inQ equiv"""
        super().__init__()
        self.fromClientQueue = requestInQ
        self.toClientQueue = clientOutQ
        self.outQ = outQ
        self.inQ = inQ
        self.N = N
        self.ldr = ldr
        self.ID = ID
        self.lastm = self.ID
        self.daemon = True
        self.inboundLock = threading.Lock()
        self.lastCommittedVal = None
        self.timeout = timeout


    def run(self):
        print("Starting paxos Protocol...")

        while "Cats" != "Dogs":


            # 1. Check for client requests:
                #2. If we have a request from a client, generate a proposal, and send it to leader
            self.clientRequestHandler()

            # 3. Check for proposals in the inProposalQueue
                # 4. If we got a proposal, run synod
            if self.countMessagesOfType("PROPOSAL") > 0:
                print("Proposer: Received proposal message, I am the leader, executing Synod")
                self.current_proposal_message = self.getMessageOfType("PROPOSAL")

                curCal = self.lastCommittedVal
                propCal = self.current_proposal_message.accVal

                isConflict = False
                if curCal is not None:
                    for curEvt in curCal.cal:
                        for propEvt in propCal.cal:
                            if (curEvt.willEventConflict(propEvt)):
                                isConflict = True
                                break
                        if isConflict is True:
                            break

                if not isConflict:
                    accNum, accVal,success = self.execSynod()
                else:
                    success = False
                    accNum = None
                    accVal = self.lastCommittedVal

                #5. Return proposal results to the requesting proposer
                resultMessage = MessDef.NetMess(messType="RESULT", recipient=self.current_proposal_message.sender,
                                                sender=self.ldr.myIP, m = self.current_proposal_message.m, accNum = accNum, accVal=accVal)
                self.addToOutQ((resultMessage,self.current_proposal_message.sender))

            # 6. Check for results in resultQ. If there are any, relay them to client (along with updated calendar)
            curResultMessage = self.getMessageOfType("RESULT")
            if curResultMessage is not None:
                success = curResultMessage.messType
                accVal = curResultMessage.accVal

                if success is False:
                    print("Proposer: paxos Failed, returning updated calendar to client")
                elif success is True:
                    print("Proposer: paxos Success, returning updated calendar to client")
                self.toClientQueue.put(success, accVal)


    def addToOutQ(self, message):
        # print("Proposer: Adding to my out Queue")
        if isinstance(message, tuple):
            
            msg0 = message[0].pickleMe()
            msg1 = message[1]

            message = (msg0, msg1)
        else:
            message = message.pickleMe()

        self.outQ.put(message)


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

        except:
            result = None

        return result

    def countMessagesOfType(self,messageType):
        v = self.getMessagesOfType(messageType)
        ct = len(v)
        for em in v:
            self.inQ.put(em)
        return ct

    def clientRequestHandler(self):
        """1. Check for client requests:
        #2. If we have a request from a client, generate a proposal, and send it to leader"""
        if self.fromClientQueue.qsize() > 0:
            print("Proposer: Got request from client, forwarding to leader")
            proposalM = MessDef.NetMess(messType="PROPOSAL", recipient=self.ldr.clIP, sender = self.ldr.myIP,
                                        m=self.chooseNewPropNum(self.lastm), accNum=-1, accVal=self.fromClientQueue.get().accVal)
            self.addToOutQ((proposalM,self.ldr.clIP))



    def chooseNewPropNum(self,lastm):
        nextm = lastm + self.N
        return nextm


    def waitForMajorityPromise(self):
        return self.waitForMajority("PROMISE")

    def waitForMajorityAck(self):
        return self.waitForMajority("ACK")

    def waitForMajority(self, messageType):
        ct = 0
        v = []
        while len(v) < self.N/2 and ct < self.timeout:
            # move the incomming queue messages to the waiting messages, check for old server messages ###
            sleep(1)
            ct += 1
            tmp = self.getMessagesOfType(messageType)
            for x in tmp:
                v.append(x)
        print()
        return v, len(v) > self.N/2


    def execSynod(self):

        nextm = self.chooseNewPropNum(self.lastm)


        #Send prepare message with nextm to all other nodes' acceptors

        print("Proposer: Sending prepare messages...")

        prepMess = MessDef.NetMess(messType = "PREPARE", sender = self.ldr.myIP, m = nextm)
        pickledPrepMess = prepMess.pickleMe()

        self.outQ.put(pickledPrepMess)


        # print("Proposer: Prepare messages put in queue!")


        #check queue, wait for majority of promise(accNum, accVal)
            #if majority, send accept to all other nodes' acceptors
            #else start over

        # print("Proposer: Waiting for promises...")

        print("Proposer: Waiting for majority promises")
        list_of_messages,promise_result = self.waitForMajorityPromise()

        #for t in range(0,timeout):
        #   print("Waiting... %i/%i"%(t+1, timeout))
        #   sleep(1)

        if not promise_result:
            print("Proposer: Majority promise not achieved")
            retAccNum= None
            retAccVal= self.lastCommittedVal
            retSuccess= False
            return retAccNum, retAccVal, retSuccess

        #Otherwise you can move on now and send accept to all other nodes acceptors
        print("Proposer: Majority promise recieved")

        #Collect all promise messages and get the largest accnNum value
        # maxAccNumVal = (0, "")
        # while proposerIn.qzise() > 0:
        #     tempMess = proposerIn.get()
        #     tempNum = tempMess.accNum
        #
        #     if tempNum > maxAccNumVal[0]:
        #         maxAccNumVal = (tempNum, tempMess.accVal)


        maxAccNumVal = (-1, "")
        for mess in list_of_messages:
            if mess.accNum > maxAccNumVal[0]:
                maxAccNumVal = (mess.accNum, mess.accVal)


        print("Proposer: Sending accept messages...")

        acceptMess = MessDef.NetMess(messType = "ACCEPT", sender = self.ldr.myIP, m = nextm, accVal = maxAccNumVal[1])
        pickledAcceptMess = acceptMess.pickleMe()

        self.outQ.put(pickledAcceptMess)

        #check queue, wait for majority of ack(accNum,accVal)
            #if majority, send commit(v) to all other nodes' acceptors

        # print("Proposer: Accept messages put in queue!")

        print("Proposer: Waiting for majority ack:")

        list_of_messages,ack_result = self.waitForMajorityAck()


        if not ack_result:
            print("Proposer: Majority ack not achieved")
            retAccNum= None
            retAccVal= self.lastCommittedVal
            retSuccess= False
            return retAccNum, retAccVal, retSuccess

        print("Proposer: Majority ack recieved")

        #commitMessages = createBroadcastMessArray(messType = 'commit', N = self.N, sender = self.ID, accVal = maxAccNumVal[1])


        print("Proposer: Sending commit messages...")

        commitMess = MessDef.NetMess(messType = "COMMIT", sender = self.ldr.myIP, m = nextm, accVal = maxAccNumVal[1])
        pickledCommitMess = commitMess.pickleMe()

        self.outQ.put(pickledCommitMess)
        self.lastm = nextm

        return maxAccNumVal[0], maxAccNumVal[1],True









