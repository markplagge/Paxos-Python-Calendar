import unittest
from leader.Leader import Leader,LeaderMessage
import simplenetwork
import asyncio
try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair




class Test_leadershipTest(unittest.TestCase):
    def setUp(self):
        pass
    def testLeadership(self):
        pass

if __name__ == '__main__':
    #unittest.main()
    #set up servers:
    pass

