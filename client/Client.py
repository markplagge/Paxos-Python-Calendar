import threading
import paxos.Acceptor
import paxos.Proposer
import paxos.gcd
import leader.Leader
import leader.NeilsQueueChecker
import queue
import simplenetwork
import pCalendar.UserCal
from PromptHelper import addEventParsing, deleteEventParsing
from MessDef import NetMess
import time
import copy
import leader.NeilLeader

class Client(threading.Thread):

    def __init__(self, N=1, pID=1, hostFile=None):
        super().__init__()
        # if hostFile is None:
        #     simplenetwork.serverData.udpDests = ["127.0.0.1"]
        #     simplenetwork.serverData.tcpDests["127.0.0.1"] = 8888

        self.timeout = 60

        svr = simplenetwork.Servers.startupServers(hostFile)

        self.uID = pID

        self.locCalendar = pCalendar.UserCal.Calendar(username=pID)

        self.inUDP = simplenetwork.serverData.mainServerQueue.inUDP
        self.outUDP = simplenetwork.serverData.mainServerQueue.outUDP

        self.inTCP = simplenetwork.serverData.mainServerQueue.inTCP #Goes to leader
        self.outTCP = simplenetwork.serverData.mainServerQueue.outTCP #Goes to leader

        self.queueChecker = leader.NeilsQueueChecker.QueueChecker(self.inUDP)
        self.queueChecker.daemon = True
        self.queueChecker.start()


        pidDict = simplenetwork.serverData.tcpDests

        pidList = range(0,N)


        nodeIPs = []
        for id in pidList:
            nodeIPs.append(pidDict[str(id)])



        #Create your node's Leader Process
        self.ldrObj = leader.NeilLeader.Representative(pid=self.uID,N=N,outQ=self.outTCP,inQ=self.inTCP,otherPIDs=pidList,otherIPs=nodeIPs,myIP=nodeIPs[self.uID])
        # self.ldrObj = leader.Leader.Leader(outQ=self.outTCP,inQ=self.inTCP,pid=self.uID,otherPIDs=pidList, otherIPs=nodeIPs, myIP=simplenetwork.serverData.tcpDests[str(pID)])

        # # TESTING WITHOUT LEADER
        # self.ldrObj.clIP = '54.174.47.231'
        # if self.uID == 4:
        #     self.ldrObj.isCurrentLeader = True
        # else:
        #     self.ldrObj.isCurrentLeader = False

        ##Start up the leader:
        self.ldrObj.daemon = True
        self.ldrObj.start()

        if self.uID == 0:
            print("Waiting for you to start up everyone for Leader Election Initialized")
            time.sleep(30)
            self.ldrObj.election()
        # self.ldrObj.clIP = '45.47.149.217'

        #Create your node's Proposer Process
        self.propInQ = queue.Queue()
        self.propOutQ = self.outUDP

        self.clientToPropQ = queue.Queue()
        self.propToClientQ = queue.Queue()

        self.propObj = paxos.Proposer.Proposer(self.propInQ, self.propOutQ, self.clientToPropQ, self.propToClientQ, N= N, ID= pID, ldr=self.ldrObj)
        self.propObj.setDaemon(True)
        self.propObj.start()

        #Create your node's Acceptor Process
        self.acceptInQ = queue.Queue()
        self.acceptOutQ = self.outUDP
        self.acceptObj = paxos.Acceptor.Acceptor(outQ =self.acceptOutQ, inQ =self.acceptInQ, ldr = self.ldrObj, thisIP=self.ldrObj.myIP, thisPort='7777')
        self.acceptObj.setDaemon(True)
        self.acceptObj.start()

        #Create your node's Grand Central Dispatch
        gcdObj = paxos.gcd.GCD(inQ=self.inUDP, propQ=self.propInQ, acceptQ=self.acceptInQ)
        gcdObj.setDaemon(True)
        gcdObj.start()

        self.daemon = True


    def execClient(self):
        running = True
        while running:

            prompt1 = "\n\n1. View your calendar\n"
            prompt2 = "2. Add an event to your local calendar\n"
            prompt3 = "3. Delete an event from your calendar\n"
            prompt4 = "4. Check the leader\n"
            prompt5 = "5. Check your ID and IP\n"
            prompt6 = "6. Reintroduce yourself to the network"

            print(prompt1 + prompt2 + prompt3 + prompt4 + prompt5 + prompt6)
            choice = int(input("What would you like to do?\n"))

            if choice == 1: #Print the events in the calendar
                print('This calendar has the following events in it:')
                self.locCalendar = copy.deepcopy(self.acceptObj.learner.ccal)


                numEvents = len(self.locCalendar.cal)

                for i in range(0,numEvents):
                    print('\t%i. '%(i) + str(self.locCalendar.cal[i]))
                print('------------\n\n')

            elif choice == 2: #Add event to calendar
                newEvent = addEventParsing(self,test=False)

                (fail, _) = self.locCalendar.addEntry(newEvent)

                if not fail:
                    #Create REQUEST message, send it to the node's proposer
                    rqstMess = NetMess(messType= "REQUEST", accVal=self.locCalendar)

                    self.clientToPropQ.put(rqstMess)

                    print("Client: Waiting for Response")
                    self.waitForResponse()

                print('------------\n\n')



            elif choice == 3: #Remove event from calendar
                eventToDelete = deleteEventParsing(self.locCalendar)

                self.locCalendar.removeEntry(eventToDelete)

                rqstMess = NetMess(messType= "REQUEST", accVal=self.locCalendar)

                self.clientToPropQ.put(rqstMess)
                print("Client: Waiting for Response")
                self.waitForResponse()

                print('------------\n\n')

            elif choice == 4:
                print(self.ldrObj.clIP)

                print('------------\n\n')

            elif choice == 5:
                print('ID: %i, IP: %s'%(int(self.uID), self.ldrObj.myIP))

                print('------------\n\n')

            elif choice == 6:
                self.ldrObj.election()

            elif choice == 0: #Add test event
                newEvent = addEventParsing(self,test=True)

                (fail, _) = self.locCalendar.addEntry(newEvent)

                if not fail:
                    rqstMess = NetMess(messType= "REQUEST", accVal=self.locCalendar)

                    self.clientToPropQ.put(rqstMess)

                    print("Added Test Event")

                    print("Client: Waiting for Response")
                    self.waitForResponse()




    def waitForResponse(self):
        responseReceived = False
        ct = 0
        while responseReceived == False and ct < self.timeout:
            if self.propToClientQ.qsize() > 0:
                print("Client: Response Recieved!")
                responseReceived = True
                response = self.propToClientQ.get()

                # if response[1] == None:
                #     # self.locCalendar = pCalendar.UserCal.Calendar(username=self.uID)
                #     self.locCalendar = copy.deepcopy(self.acceptObj.learner.ccal)
                #
                #
                # if response[0] == True: #SUCCESS!!!
                #     # self.locCalendar = response[1]
                #     self.locCalendar = copy.deepcopy(self.acceptObj.learner.ccal)

            ct += 1
            time.sleep(1)

        if responseReceived == False:
            #Lost connection with leader, initiate election
            self.ldrObj.election()
