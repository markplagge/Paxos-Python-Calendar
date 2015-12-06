import threading
import paxos.Acceptor
import paxos.Proposer
import paxos.gcd
import leader.Leader
import queue
import simplenetwork
import pCalendar.UserCal
from PromptHelper import addEventParsing, deleteEventParsing
from MessDef import NetMess
import time

class Client(threading.Thread):

    def __init__(self,hosts, N=1, pID=1, hostFile=None):
        super().__init__()
        if hostFile is None:
            simplenetwork.serverData.udpDests = ["127.0.0.1"]
            simplenetwork.serverData.tcpDests["127.0.0.1"] = 8888

        self.timeout = 30

        svr = simplenetwork.Servers.startupServers(hostFile)

        self.uID = pID

        self.locCalendar = pCalendar.UserCal.Calendar(username=pID)

        self.inUDP = simplenetwork.serverData.mainServerQueue.inUDP
        self.outUDP = simplenetwork.serverData.mainServerQueue.outUDP

        self.inTCP = simplenetwork.serverData.mainServerQueue.inTCP #Goes to leader
        self.outTCP = simplenetwork.serverData.mainServerQueue.outTCP #Goes to leader


        #Create your node's Leader Process
        self.ldrObj = leader.Leader.Leader(outQ=self.outTCP,inQ=self.inTCP)

        ##Start up the leader:
        self.ldrObj.daemon = True
        self.ldrObj.start()

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
        self.acceptObj = paxos.Acceptor.Acceptor(outQ =self.acceptOutQ, inQ =self.acceptInQ, ldr = self.ldrObj, thisIP=self.ldrObj.myIP, thisPort=self.ldrObj.myIP)
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
            prompt4 = "4. Refresh\n"

            print(prompt1 + prompt2 + prompt3 + prompt4)
            choice = int(input("What would you like to do?\n"))

            if choice == 1: #Print the events in the calendar
                print('This calendar has the following events in it:')

                numEvents = len(self.locCalendar.cal)

                for i in range(0,numEvents):
                    print('\t%i. '%(i) + str(self.locCalendar.cal[i]))
                print('------------\n\n')

            elif choice == 2: #Add event to calendar
                newEvent = addEventParsing(self)

                (succ, _) = self.locCalendar.addEntry(newEvent)

                if succ:
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

            elif choice == 4: #Check for RESULTs from proposer
                print("YOU DID NOTHING YOU DINGBAT")

                print('------------\n\n')

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

                self.locCalendar = response[1]
            ct += 1
            time.sleep(1)




if __name__ == '__main__':
    print("Starting")
    theClient = Client(1)

    theClient.execClient()