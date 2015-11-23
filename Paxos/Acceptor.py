import threading
import queue
import leader.Leader
import paxosObjs

#Global Acceptor Queue:

acceptorIn = queue.Queue()
acceptorOut = queue.Queue()

class Acceptor(threading.Thread):
    """represents an accecptor in Paxos. Is threaded."""
    def __init__(self, daemon = True, outQ = queue.Queue(), inQ = queue.Queue(), ldr = leader.Leader()):
        self.daemon = daemon
        self.outQ = outQ
        self.inQ = inQ

        self.ldr = ldr

        return super().__init__()
    
    def run(self):
        while(True):
            if acceptorIn.qsize() > 0:
                dest = self.ldr.clIP


