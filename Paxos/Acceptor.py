import threading
import queue
import leader.Leader


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

        self.latestPromise = 0
        self.latestPromiseData = None

        return super().__init__()
    
    def newPromise(pNum, Pval):
        """Runs when the incomming suggested value is bigger than the current promised value"""
        pass
    def extractMessage(msg):
        return msg[0],msg[1] 
    def run(self):
        while(True):
            if acceptorIn.qsize() > 0:
                dest = self.ldr.clIP
                prID,dat = acceptorIn.get()
                if self.latestPromise < prID:
                    self.newPromise(prID,dat)
                else:
                    pass



