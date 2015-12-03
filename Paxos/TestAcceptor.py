import unittest
import paxos.Acceptor
from queue import Queue as Q
## Tests some functions of the acceptor.

class testAccept(unittest.TestCase):
    def setUp(self):
        self.inQ = Q()
        self.outQ = Q()
        self.acpt = paxos.Acceptor.Acceptor(outQ= self.outQ, inQ=self.inQ, thisIP="127.0.0.1")
    def testAcceptInit(self):
        print("init is done")
        assert self.acpt.myIP == "127.0.0.1"