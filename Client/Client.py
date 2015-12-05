import threading
import Paxos.Acceptor
import Paxos.Proposer
import Paxos.GCD
import simplenetwork
import leader.Leader
import queue.Queue
import pCalendar.UserCal

class Client(threading.Thread):

    def __init__(self,hosts, N=1, pID=1):
        self.uID = pID

        self.locCalendar = pCalendar.UserCal.Calendar(username=pID)

        inUDP = simplenetwork.serverData.inUDP
        outUDP = simplenetwork.serverData.outUDP

        inTCP = simplenetwork.serverData.inTCP #Goes to leader
        outTCP = simplenetwork.serverData.outTCP #Goes to leader


        #Create your node's Leader Process
        self.ldrObj = leader.Leader.Leader(outQ=outTCP,inQ=inTCP)


        #Create your node's Proposer Process
        propInQ = queue.Queue()
        propOutQ = queue.Queue()

        self.clientToPropQ = queue.Queue()
        self.propToClientQ = queue.Queue()

        self.propObj = Paxos.Proposer.Proposer(propInQ,propOutQ,self.clientToPropQ, self.propToClientQ, N= N, ID= pID, ldr=self.ldrObj)

        #Create your node's Acceptor Process
        acceptInQ = queue.Queue()
        acceptOutQ = queue.Queue()
        self.acceptObj = Paxos.Acceptor.Acceptor(outQ = acceptOutQ, inQ = acceptInQ, ldr = self.ldrObj, thisIP=self.ldrObj.myIP, thisPort=self.ldrObj.myIP)

        #Create your node's Grand Central Dispatch
        gcdObj = Paxos.GCD.GCD(inQ=inUDP, propQ=propInQ, acceptQ=acceptInQ)

    def execClient(self):
        while 'cats' != 'dogs':
            prompt1 = "1. View your calendar\n"
            prompt2 = "2. Add an event to your local calendar\n"
            prompt3 = "3. Delete an event from your calendar\n"

            print(prompt1 + prompt2 + prompt3)
            choice = int(input("What would you like to do?\n"))

            if choice == 1: #Print the events in the calendar
                print('This calendar has the following events in it:')

                numEvents = len(self.theCalendar.cal)

                for i in range(0,numEvents):
                    print('\t%i. '%(i) + str(self.theCalendar.cal[i]))
                print('------------\n\n')

            elif choice == 2: #Add event to calendar
                newEvent = addEventParsing(self)
                parts = newEvent.participants
                outboundEvents = []

                algHelper.alginsert(self,newEvent)

                for i in parts:
                    if i is not self.uid:
                        algHelper.algsend(self,i) #Notify of the new insert that concerns them

                print('------------\n\n')
                return outboundEvents
            elif choice == 3: #Remove event from calendar
                eventToDelete = deleteEventParsing(self.theCalendar)
                parts = eventToDelete.participants


                algHelper.algdelete(self,eventToDelete)

