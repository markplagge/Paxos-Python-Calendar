import threading
import sys
import queue;
import pickle

class LeaderMessage(object):
    def __init__(self, pid,num,ip,port):
        self.pid = pid
        self.reqNum = num
        self.sourceIP = ip
        self.sourcePort = port
class PingMessage(object):
    def __init__(self, sourceIP):
        self.sourceIP = sourceIP

class OkMess(PingMessage):
    def __init__(self, sourceIP):
        return super().__init__(sourceIP)
class queryMess(PingMessage):
    def __init__(self, sourceIP):
        return super().__init__(sourceIP)

 
class Leader(threading.Thread):

    """Leader represents the leadership role in the program. It
    will poll other servers and ask them for information. It also
    checks to see if TCP data has arrived, and if so """
    isCurrentLeader = True
    def __init__(self, outQ = queue.Queue(), inQ = queue.Queue(),
                 pid = 0, myIP="127.0.0.1", myPort=8888, **kwargs):
        super().__init__()
        self.outQ = outQ
        self.inQ = inQ
        self.liveQs = []
        self.pid = pid
        self.daemon = True
        self.inMessages = []
        self.myIP = myIP
        self.myPort = myPort
        
        self.clIP = "127.0.0.1"
        self.clP = 7777
        self.live = ""
        self.currentTick = 0
        self.timeout = 10
    def checkData(self):
        if self.inQ.qsize() > 0:
            itm = self.inQ.get()
            obj = pickle.loads(itm)
            self.inMessages.append(obj)
    def ttime(self):
        print("Tick...")
        self.currentTick += 1
        if self.currentTick % 5 == 0:
            self.checkLive()
        threading.Timer(1,self.ttime).start()

     
    def elect(self):
        self.outQ.put(pickle.dumps(LeaderMessage(self.pid,0,self.myIP,self.myPort),protocol=pickle.HIGHEST_PROTOCOL))

    def liveTimeoutCheck(self):
        timeouts = False
        for lq in self.liveQs:
            if self.currentTick - lq[0] > self.timeout:
                timeouts = True
        return timeouts

    def checkLive(self):
        if not self.isCurrentLeader:
            self.outQ.put(pickle.dumps((queryMess(self.myIP),self.clIP)))
            self.liveQs.append((self.currentTick,self.clIP))


    def okResp(self,dip):
        self.outQ.put(((OkMess(self.myIP),self.clIP),dip))
        
    def dataHandler(self):
        for m in self.inMessages:
            if isinstance(m,queryMess):
                self.okResp(m.sourceIP)
            elif isinstance(m,LeaderMessage):
                if m.pid > self.pid:
                    self.isCurrentLeader = True
                    self.outQ.put(pickle.dumps(LeaderMessage(self.pid,0,self.myIP,self.myPort)))


    def run(self):
        self.live = threading.Timer(1,self.ttime)
        self.live.start()
        self.elect()
        while(True):
            self.checkData()
           
            if self.liveTimeoutCheck() :
                self.elect()



def main():
    inQ = queue.Queue()
    outQ = queue.Queue()
    ldr = Leader(myIP="localhost",inQ=inQ, outQ = outQ)

    ld2 = Leader(myIP="OTHER",pid=1)
    ldr.start()
    ld2.start()
    lm = pickle.dumps(LeaderMessage(1,0,"loclall",123),protocol=pickle.HIGHEST_PROTOCOL)
    inQ.put(lm)

    while True:
        pass

    


if __name__ == "__main__":
    sys.exit(int(main() or 0))