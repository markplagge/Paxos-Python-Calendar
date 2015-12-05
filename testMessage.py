import unittest
import MessDef
def wrd():
    import datetime
    from numpy import random as random

    return datetime.datetime(random.randint(1970, 2014),
                             random.randint(1, 10),
                             random.randint(1, 20))
def createCE(self):
    import datetime
    from numpy import random as random
    import itertools
    from pCalendar.UserCal import CalEvent



    startDates = []
    endDates = []

    fns = ["bob", "john", "ringo", "Paul", "Conan", "Mike"]
    lns = ["Mario", "Luigi", "Walker", "LaQuarius", "Edmond", "Aadams"]
    rnks = ["pleb", "midLevel", "CEO"]

    self.events = []
    fullNames = [fns, lns]
    self.employeeList = []

    for list in itertools.product(*fullNames):
        self.employeeList.append(list)
    # going to use about 50% overlap events for test:
    startD = 1
    startE = 4
    for _ in range((int(len(self.employeeList) / 2))):
        startDates.append(datetime.datetime(2016, 1, startD,
                                            random.randint(1, 10),
                                            random.randint(1, 5),
                                            random.randint(1, 50)))
        endDates.append(datetime.datetime(2016, 1, startE,
                                          random.randint(1, 10),
                                          random.randint(1, 5),
                                          random.randint(1, 50)))
        startD += 1
        startE += 1
    for _ in range((len(self.employeeList))):
        sd = (wrd())
        startDates.append(sd)
        endDates.append(sd + datetime.timedelta(5))

    for i in range(len(self.employeeList)):
        self.events.append(CalEvent(startDates[i], endDates[i], self.employeeList[i][0],
                                    self.employeeList[i][1], random.choice(rnks), "NONE"))
    self.startDates = startDates
    self.endDates = endDates
    self.createdFiles = []
class TestPickle(unittest.TestCase):

    def tearDown(self):
        for fn in self.createdFiles:
            os.remove(fn)
    def createMessage(self,cal):
        from numpy import random as rnd
        msg = MessDef.NetMess()
        msg.messType = rnd.choice(self.messageTypes)
        msg.recipient = rnd.choice(self.recips)
        msg.sender = rnd.choice(self.senders)
        msg.m = rnd.choice(self.m)
        msg.accNum = rnd.choice(self.accNums)
        if cal is not None:
            msg.accVal = rnd.choice(self.cals)
        return msg

    def setUp(self):
        from pCalendar.UserCal import CalEvent,Calendar
        from numpy import random as rnd
        self.messageTypes = ["PROPOSE", "PROMISE", "ACCEPT", "COMMIT", "ACK"]
        self.recips = ["127.0.0.1", "192.168.1.1"]
        self.senders = ["127.0.0.1", "192.168.1.1"]
        self.m = [1,2,3,4,5]
        self.accNums = [1,2,3,4,5]

        createCE(self)
        self.cals = []
        for i in range(0,5):
            cal = Calendar("UnitTester" + str(i))
            rnd.shuffle(self.events)
            cal.events = self.events
            self.cals.append(cal)

        ##create some messages
        self.messagesWithValue = []
        self.messagesNoValue = []
        for i in range(0,5):

            self.messagesWithValue.append(self.createMessage(""))
            self.messagesNoValue.append(self.createMessage(None))






    def testPickleWithValue(self):

        for mess in self.messagesWithValue:
            assert(isinstance(mess,MessDef.NetMess))
            pickled = mess.pickleMe()
            #print(pickled)
            depickled = MessDef.dePickle(pickled)
            assert(depickled == mess)

    def testPickleWithoutValue(self):
        for mess in self.messagesNoValue:
            assert(isinstance(mess,MessDef.NetMess))
            pickled = mess.pickleMe()
            #print(pickled)
            depickled = MessDef.dePickle(pickled)
            assert(depickled == mess)

if __name__ == '__main__':
    unittest.main()
