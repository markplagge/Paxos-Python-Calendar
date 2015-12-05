import threading
import Paxos.Acceptor
import Paxos.Proposer
import Paxos.GCD
import leader.Leader
import queue
import simplenetwork
import pCalendar.UserCal
from PromptHelper import addEventParsing, deleteEventParsing
from MessDef import NetMess

class Client(threading.Thread):

    def __init__(self,hosts, N=1, pID=1):
        super().__init__()

        svr = simplenetwork.Servers.startupServers()

        self.uID = pID

        self.locCalendar = pCalendar.UserCal.Calendar(username=pID)

        inUDP = simplenetwork.serverData.mainServerQueue.inUDP
        outUDP = simplenetwork.serverData.mainServerQueue.outUDP

        inTCP = simplenetwork.serverData.mainServerQueue.inTCP #Goes to leader
        outTCP = simplenetwork.serverData.mainServerQueue.outTCP #Goes to leader


        #Create your node's Leader Process
        self.ldrObj = leader.Leader.Leader(outQ=outTCP,inQ=inTCP)


        #Create your node's Proposer Process
        propInQ = queue.Queue()
        propOutQ = queue.Queue()

        self.clientToPropQ = queue.Queue()
        self.propToClientQ = queue.Queue()

        self.propObj = Paxos.Proposer.Proposer(propInQ,propOutQ,self.clientToPropQ, self.propToClientQ, N= N, ID= pID, ldr=self.ldrObj)
        self.propObj.setDaemon(True)
        self.propObj.start()

        #Create your node's Acceptor Process
        acceptInQ = queue.Queue()
        acceptOutQ = queue.Queue()
        self.acceptObj = Paxos.Acceptor.Acceptor(outQ = acceptOutQ, inQ = acceptInQ, ldr = self.ldrObj, thisIP=self.ldrObj.myIP, thisPort=self.ldrObj.myIP)
        self.acceptObj.setDaemon(True)
        self.acceptObj.start()

        #Create your node's Grand Central Dispatch
        gcdObj = Paxos.GCD.GCD(inQ=inUDP, propQ=propInQ, acceptQ=acceptInQ)

        self.daemon = True


    def execClient(self):
        while 'cats' != 'dogs':

            prompt1 = "1. View your calendar\n"
            prompt2 = "2. Add an event to your local calendar\n"
            prompt3 = "3. Delete an event from your calendar\n"
            prompt4 = "4. Refresh"

            print(prompt1 + prompt2 + prompt3)
            choice = int(input("What would you like to do?\n"))

            if choice == 1: #Print the events in the calendar
                print('This calendar has the following events in it:')

                numEvents = len(self.locCalendar.cal)

                for i in range(0,numEvents):
                    print('\t%i. '%(i) + str(self.locCalendar.cal[i]))
                print('------------\n\n')

            elif choice == 2: #Add event to calendar
                newEvent = addEventParsing(self)

                self.locCalendar.addEntry(newEvent)

                #Create REQUEST message, send it to the node's proposer
                rqstMess = NetMess(messType= "REQUEST", accVal=self.locCalendar)

                self.clientToPropQ.put(rqstMess)


                print('------------\n\n')



            elif choice == 3: #Remove event from calendar
                eventToDelete = deleteEventParsing(self.locCalendar)

                self.locCalendar.removeEntry(eventToDelete)

                rqstMess = NetMess(messType= "REQUEST", accVal=self.locCalendar)

                self.clientToPropQ.put(rqstMess)


                print('------------\n\n')

            elif choice == 4: #Check for RESULTs from proposer
                print("YOU DID NOTHING YOU DINGBAT")

                print('------------\n\n')





if __name__ == '__main__':
    print("Starting")
    theClient = Client(1)

    theClient.execClient()