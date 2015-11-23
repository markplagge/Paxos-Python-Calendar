import queue
import asyncio
import threading
import unittest
import pCalendar
import LogParser
import simplenetwork
import random
import time
import sys
import concurrent
x = queue.Queue()

class test(object):

    def __init__(self, q):
        self.q = q



class test2(object):
    def __init__(self, q):
        self.q = q;



t1 = test(x)
t2 = test2(x)

t1.q.put("TEST!!")
print(t2.q.get())

@asyncio.coroutine
def getInput():

    while True:
        data = input("enter data:")
        yield from asyncio.sleep(2)

## use this to stop TCP timeout waits:
#try:
#    #Servers.startupThreadedServers()
#    loop = asyncio.get_event_loop()
#    thread = threading.Thread()
#    #coro = loop.call_soon_threadsafe(loop.run_in_executor,thread,Servers.startupServers)
#    #loop.call_soon(Servers.startupServers)
#    tcpserver = Servers.startupServers()
#    loop.run_until_complete(getInput())

#    loop.run_until_complete(tcpserver)


#    #asyncio.ensure_future(coro)


#except KeyboardInterrupt:
#    Servers.closeServers()

def threadwaiter(sent=2):
    while simplenetwork.serverData.mainServerQueue.inTCP.qsize() < sent:
        time.sleep(3)
    while simplenetwork.serverData.mainServerQueue.inUDP.qsize() <sent:
        time.sleep(3)


def serverRun():
    coro = simplenetwork.Servers.startupServers()
    loop = asyncio.get_event_loop()
    
    tcpServer = loop.run_until_complete(coro)
    time.sleep(2)
    simplenetwork.Servers.startSender()
    #simplenetwork.TCPio.main()
   
 

class TestCalEvents(unittest.TestCase):
    def testEQ(self):
        x = pCalendar.UserCal.Calendar(158)
        evt1 = pCalendar.UserCal.CalEvent()
        evt2 = evt1.clone()
        assert (evt1 == evt2)

class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.logger = LogParser.LogE(fileName = "testMe.csv",userID="BobbyTest")
        simplenetwork.serverData.udpDests = ["127.0.0.1"]
        simplenetwork.serverData.udpPort = random.randint(6000,9000)
        simplenetwork.serverData.tcpPort = random.randint(2000,5444)
        simplenetwork.serverData.tcpDests = ["127.0.0.1"]
        self.qs = simplenetwork.serverData.mainServerQueue

    def testAdd(self):
        x = pCalendar.UserCal.CalEvent()
        self.logger.addAppend(x)
        print(self.logger.generateCal())
        print("Completed testAdd")
        
        return True
    def testDel(self):
        x = pCalendar.UserCal.CalEvent(eventName="DELETE ENTRY TEST")
        
        uid = self.logger.addAppend(x)
        cal = self.logger.generateCal()
        isT = False
        print(cal)
        self.logger.addDelete(cal.cal[0], uid)
        print(self.logger.generateCal())

    def testUDPBroadcast(self):

        srv, snd = simplenetwork.UDPio.testUDP()
        
        self.qs.outUDP.put("Test Value")
        
        while self.qs.inUDP.qsize() < 1:
            pass
        assert self.qs.inUDP.get() == "Test Value"
        srv.shutdown()
        simplenetwork.UDPio.sndrRun = False

    def testUDPSingle(self):
        srv, snd = simplenetwork.UDPio.testUDP()
        self.qs.outUDP.put(("Test Value", "127.0.0.1"))
        while self.qs.inUDP.qsize() < 1:
            pass
        assert self.qs.inUDP.get() == "Test Value"
        srv.shutdown()
        simplenetwork.UDPio.sndrRun = False
    
    def testServerInit(self):
        exec = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        bc = "broadcast test string"
        sc = "single test string"
        self.qs.outUDP.put(bc)
        self.qs.outUDP.put((sc,"127.0.0.1"))
        self.qs.outTCP.put(bc)
        self.qs.outTCP.put((sc,"127.0.0.1"))
        loop = asyncio.get_event_loop()
        x = threading.Thread(target=threadwaiter)
        x.start()
        #v = threading.Thread(target=serverRun)
        #v.start()
        loop.run_in_executor(executor = exec,func=serverRun())
        x.join()

        while self.qs.inTCP.qsize() > 0:
            ind = self.qs.inTCP.get()
            assert(ind == bc or ind == sc)
            print("TCP Data got: " + ind)
        while self.qs.inUDP.qsize() > 0:
            ind = self.qs.inUDP.get()
            assert(ind == bc or ind == sc)
            print("UDP Data got: " + ind)
        loop.close()
        #simplenetwork.Servers.running = False
        #asyncio.async(simplenetwork.Servers.closeServers)
        #asyncio.async(simplenetwork.Servers.closeServers())


"""
class TestCalEvents(unittest.TestCase):
    def testEQ(self):
        x = pCalendar.UserCal.Calendar(158)
        evt1 = pCalendar.UserCal.CalEvent()
        evt2 = evt1.clone()
        assert (evt1 == evt2)

class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.logger = LogParser.LogE(fileName = "testMe.csv",userID="BobbyTest")

    def testAdd(self):
        x = pCalendar.UserCal.CalEvent()
        self.logger.addAppend(x)
        print(self.logger.generateCal())
        print("Completed testAdd")
        return True
"""


def main():
    tstr = TestLogParser()
    tstr.setUp()
    tstr.testServerInit()

if __name__ == "__main__":
    sys.exit(int(main() or 0))