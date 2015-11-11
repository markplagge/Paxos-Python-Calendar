import queue
import asyncio
import threading
import unittest
import pCalendar
import LogParser
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
    def testDel(self):
        x = pCalendar.UserCal.CalEvent(eventName="DELETE ENTRY TEST")
        
        uid = self.logger.addAppend(x)
        cal = self.logger.generateCal()
        isT = False
        print(cal)
        self.logger.addDelete(cal.cal[0], uid)
        print(self.logger.generateCal())
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