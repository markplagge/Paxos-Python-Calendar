#Neil McGlohon - Nov 22, 2015

import threading
import queue
import leader.Leader
import MessDef
import math


proposerIn = queue.Queue()
proposerOut = queue.Queue()
timeout = 5 #time to wait for queue to determine if majority has been found

class Proposer(threading.Thread):

    def __init__(self, N = 1, ID = -1, outQ = queue.Queue(), inQ = queue.Queue(), ldr = leader.Leader()):
        self.outQ = outQ
        self.inQ = inQ
        self.N = N
        self.ldr = ldr
        self.ID = ID
        self.lastm = self.ID
        return super().__init__()
    
    def run(self):
        while "Cats" != "Dogs":

            print("WE NEED INPUT FROM USER HERE RIGHT?")

            print("Starting Paxos Protocol...")

            success = self.propose()

            if success is False:
                print("Paxos Failed, Starting Over")
            else:
                print("Paxos Success! Starting Over")


    def chooseNewPropNum(lastm):
        nextm = lastm + N
        return nextm

    def propose(self):
        nextm = chooseNewPropNum(self.lastm)


        #Send prepare message with nextm to all other nodes' acceptors

        #create message
        prepMessages = createBroadcastMessArray(messType = 'prepare', N = self.N, sender = self.ID, m = self.nextm)

        print("Sending prepare messages...")
        for i in range(0,len(prepMessages)):
            proposerOut.put(prepMessages[i])



        #check queue, wait for majority of promise(accNum, accVal)
            #if majority, send accept to all other nodes' acceptors
            #else start over

        print("Waiting for promises...")
        for t in range(0,timeout):
            print("Waiting... %i/%i"%(t+1, timeout))
            sleep(1)

        print("Done waiting, checking for majority promises")

        """THIS IS WRONG, YOU COULD HAVE WHO KNOWS WHAT IN THE QUEUE, NOT JUST ONE TYPE SO WE'RE COUNTING THE NUMBER OF MESSAGES NOT JUST AMOUNT OF TYPE"""
        if proposerIn.qsize() < math.ceil(N/2):            
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


        acceptMessages = createBroadcastMessArray(messType = 'accept', N = self.N, sender = self.ID, m = nextm, accVal = maxAccNumVal[1])

        print("Sending accept messages...")
        for i in range(0,len(acceptMessages)):
            proposerOut.put(acceptMessages[i])


        #check queue, wait for majority of ack(accNum,accVal)
            #if majority, send commit(v) to all other nodes' acceptors

        print("Waiting for acks...")
        for t in range(0,timeout):
            print("Waiting... %i/%i"%(t+1, timeout))
            sleep(1)

        print("Done waiting, checking for majority acks")

        """THIS IS WRONG, YOU COULD HAVE WHO KNOWS WHAT IN THE QUEUE, NOT JUST ONE TYPE SO WE'RE COUNTING THE NUMBER OF MESSAGES NOT JUST AMOUNT OF TYPE"""
        if proposerIn.qsize() < math.ceil(N/2):            
            #you failed to get majority response
            return False


        print("Majority ack recieved")

        commitMessages = createBroadcastMessArray(messType = 'commit', N = self.N, sender = self.ID, accVal = maxAccNumVal[1])


        print("Sending commit messages...")
        for i in range(0,len(commitMessages)):
            proposerOut.put(commitMessages[i])

        return True









