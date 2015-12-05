import unittest


class TetAcceptor(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
    class testAcceptor(unittest.TestCase):
    def setUp(self):
        import datetime
        from numpy import random as random
        import itertools
        from pCalendar.UserCal import CalEvent,Calendar



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
            sd = (self.wrd())
            startDates.append(sd)
            endDates.append(sd + datetime.timedelta(5))

        for i in range(len(self.employeeList)):
            self.events.append(CalEvent(startDates[i], endDates[i], self.employeeList[i][0],
                                        self.employeeList[i][1], random.choice(rnks), "NONE"))
        self.startDates = startDates
        self.endDates = endDates
        self.createdFiles = []
        self.calendars = []
        for i in range(1,10):
            cal = Calendar(str(i))
            np.random.shuffle( self.events)
            cal.cal = self.events
            self.calendars.append(i,cal)

#Message long
#PREPARE ->
#PROMISE <-
#ACCEPT ->
#ACK <-
#COMMIT ->



if __name__ == '__main__':
    x = testProposal()


if __name__ == '__main__':
    unittest.main()
