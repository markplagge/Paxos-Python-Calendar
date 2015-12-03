﻿#Neil McGlohon - Nov 22, 2015

import threading
import queue
import leader.Leader
import MessDef
import math
import time.sleep as sleep

proposerIn = queue.Queue()
proposerOut = queue.Queue()
timeout = 5 #time to wait for queue to determine if majority has been found


class Proposer(threading.Thread):

    def __init__(self,inQ,outQ,requestInQ, clientOutQ,
                    ackQ, N = 1, ID = -1,  ldr = leader.Leader()):
        """Change q references later on to outQ and inQ equiv"""

        self.queueOfMessagesAndRequestsFromClientThread = requestInQ
        self.queueContainingMessagesAndDataForTheClientToProcess = clientOutQ
        self.ackQ = ackQ
        self.outQ = outQ
        self.inQ = inQ
        self.N = N
        self.ldr = ldr
        self.ID = ID
        self.lastm = self.ID
        self.daemon = True
        self.inboundLock = threading.Lock()

        super().__init__()

    def addToOutQ(self, message):
        if isinstance(message, tuple):
            message[0] = message[0].pickleMe()
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

    def clientRequestHandler(self):
        """1. Check for client requests:
        #2. If we have a request from a client, generate a proposal, and send it to leader"""
        if self.queueOfMessagesAndRequestsFromClientThread.qsize() > 0:
            proposalM = MessDef.NetMess(messType="PROPOSAL", recipient=self.ldr.clIP, sender = self.ldr.myIP,
                                        m=self.chooseNewPropNum(), accNum=-1, accVal=self.queueOfMessagesAndRequestsFromClientThread.get())
            self.addToOutQ((proposalM,self.ldr.clIP))





    def run(self):
        while "Cats" != "Dogs":

            print("WE NEED INPUT FROM USER HERE RIGHT?")

            print("Starting Paxos Protocol...")
            #1. Check for client requests:
            #2. If we have a request from a client, generate a proposal, and send it to leader
            self.clientRequestHandler()
            #3. Check for proposals in the inProposalQueue
            #4. If we got a proposal, run synod
            if self.countMessagesOfType("PROPOSAL") > 0:
                self.current_proposal_message = self.getMessageOfType("PROPOSAL")
                accNum, accVal,success = self.execSynod()
                #5. Return proposal results to the requesting proposer
                resultMessage = MessDef.NetMess(messType="RESULT", recipient=self.current_proposal_message.sender,
                                                sender=self.ldr.myIP, m = self.current_proposal_message.m, accNum = accNum, accVal=accVal)
                self.addToOutQ((resultMessage,self.current_proposal_message.sender))
            #6. Check for results in resultQ. If there are any, relay them to client (along with updated calendar)
            curResultMessage = self.getMessageOfType("RESULT")
            if curResultMessage is not None:
                self.queueContainingMessagesAndDataForTheClientToProcess.put(MessDef.NetMess(messType=success, accVal = accVal))
                #Do result message stuff here





            success = self.execSynod()

            if success is False:
                print("Paxos Failed, Starting Over")
            else:
                print("Paxos Success! Starting Over")


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
            print("Waiting... %i/%i"%(ct+1, timeout))
            # move the incomming queue messages to the waiting messages, check for old server messages ###
            sleep(1)
            ct += 1
            tmp = self.getMessagesOfType(messageType)
            for x in tmp:
                v.append(tmp)
        return v, len(v) > self.N/2


    def execSynod(self):
        nextm = self.chooseNewPropNum(self.lastm)


        #Send prepare message with nextm to all other nodes' acceptors

        #create message
        #prepMessages = createBroadcastMessArray(messType = 'prepare', N = self.N, sender = self.ID, m = self.nextm)

        print("Sending prepare messages...")
        #for i in range(0,len(prepMessages)):
        #    proposerOut.put(prepMessages[i])



        #check queue, wait for majority of promise(accNum, accVal)
            #if majority, send accept to all other nodes' acceptors
            #else start over

        print("Waiting for promises...")
        
        list_of_messages,promise_result = self.waitForMajorityPromise()

        #for t in range(0,timeout):
        #   print("Waiting... %i/%i"%(t+1, timeout))
        #   sleep(1)

        print("Done waiting, checking for majority promises")

        if proposerIn.qsize() < math.ceil(self.N/2):
            #you failed to get majority response
            return False

        #Otherwise you can move on now and send accept to all other nodes acceptors
        print("Majority promise recieved")

        #Collect all promise messages and get the largest accnNum value

        maxAccNumVal = (0, "")
        while proposerIn.qzise() > 0:
            tempMess = proposerIn.get()
            tempNum = tempMess.accNum

            if tempNum > maxAccNumVal[0]:
                maxAccNumVal = (tempNum, tempMess.accVal)


        #acceptMessages = createBroadcastMessArray(messType = 'accept', N = self.N, sender = self.ID, m = nextm, accVal = maxAccNumVal[1])

        print("Sending accept messages...")
        # for i in range(0,len(acceptMessages)):
        #     proposerOut.put(acceptMessages[i])


        #check queue, wait for majority of ack(accNum,accVal)
            #if majority, send commit(v) to all other nodes' acceptors

        print("Waiting for acks...")
        for t in range(0,timeout):
            print("Waiting... %i/%i"%(t+1, timeout))
            sleep(1)

        print("Done waiting, checking for majority acks")

        """THIS IS WRONG, YOU COULD HAVE WHO KNOWS WHAT IN THE QUEUE, NOT JUST ONE TYPE SO WE'RE COUNTING THE NUMBER OF MESSAGES NOT JUST AMOUNT OF TYPE"""
        if proposerIn.qsize() < math.ceil(self.N/2):
            #you failed to get majority response
            return False


        print("Majority ack recieved")

        #commitMessages = createBroadcastMessArray(messType = 'commit', N = self.N, sender = self.ID, accVal = maxAccNumVal[1])


        print("Sending commit messages...")
        # for i in range(0,len(commitMessages)):
        #     proposerOut.put(commitMessages[i])

        return True








