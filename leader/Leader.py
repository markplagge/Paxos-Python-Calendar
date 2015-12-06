import threading
import queue
#import multiprocessing
#import multiprocessing as threading
#from multiprocessing import queues as queue

import sys

import pickle
import asyncio
import time
class LeaderSuper(object):
    def __init__(self, pid,num,ip,port):
        self.pid = pid
        self.reqNum = num
        self.sourceIP = ip
        self.sourcePort = port

    def __str__(self):
        return "Message from pid " + str(self.pid) + ", IP: " + str(self.sourceIP)

class LeaderMessage(LeaderSuper):
    pass
   

class PingMessage(LeaderSuper):
    def __str__(self):
        return "Ping message from " + str(self.pid)

class OkMess(PingMessage):
    pass

class QueryMess(PingMessage):
    pass

class LeaderAs(object):
    isCurrentLeader = True
    electionInProgress = False
    def __init__(self,loop, outQ = queue.Queue(), inQ = queue.Queue(),
                 pid = 0, myIP="127.0.0.1", myPort=8888,timeout=5,tickTime=1):
        
        self.outQ = outQ
        self.inQ = inQ
        self.pid = pid
        self.daemon = True
        self.inMessages = []
        self.myIP = myIP
        self.myPort = myPort
        
        self.clIP = "127.0.0.1"
        self.clP = 7777
        self.live = ""
        self.currentTick = 0
        self.timeout = timeout
        self.tickTime = tickTime
        self.reqNum = 0
        self.lock = threading.Lock()
        self.running = asyncio.Event()
        self.running.set()
        self.discEvent = asyncio.Event(loop = loop)
        self.electionInProgress = asyncio.Event(loop = loop)
        self.loop = loop
    def checkData(self):
        if self.inQ.qsize() > 0:
            itm = self.inQ.get()
            obj = pickle.loads(itm)
            self.inMessages.append(obj)
    def getReqNum(self):
        with self.lock:
            x = self.reqNum
            self.reqNum += 1
        return x

    def elect(self):
        self.electionInProgress.set()
        rq = self.getReqNum()
        self.outQ.put(pickle.dumps(LeaderMessage(self.pid,rq,self.myIP,self.myPort),protocol=pickle.HIGHEST_PROTOCOL))
        #self.electTimer = threading.Timer(self.timeout,self.leadershipCheck).start()
        self.electTimer = self.loop.call_later(self.timeout,self.electionTimeout)

    def setLeader(self, leaderIP = None):
        if leaderIP is None:
            self.isCurrentLeader = True
            self.clIP = self.myIP
        else:
            self.isCurrentLeader = False
            self.clIP = leaderIP
       
    def electionTimeout(self):
        #called after the election timeout
        self.electionInProgress.clear()
        self.isCurrentLeader = True
        self.setLeader()
    
    def dataHandler(self):
        for m in self.inMessages:
            if isinstance(m,LeaderMessage):
                if m.pid < self.pid:
                    self.isCurrentLeader = True
                    cr = self.getReqNum()
                    self.outQ.put(pickle.dumps(LeaderMessage(self.pid,cr,self.myIP,self.myPort)))
                    while self.liveQs.qsize() > 0 :
                        x = self.liveQs.get()
                        self.liveQs.task_done()
                else:
                    self.isCurrentLeader = False

        self.inMessages.clear()


    @asyncio.coroutine
    def run(self):
        print("runnning leader")
        self.elect()
        while True:
            self.running.wait()
            self.checkData()
            self.dataHandler()
        
            if self.discEvent.is_set():
                self.discEvent.clear()
                self.elect()
            
            yield from asyncio.sleep(2)



    
    


class Leader(threading.Thread):
#class Leader(multiprocessing.process):

    """Leader represents the leadership role in the program. It
    will poll other servers and ask them for information. It also
    checks to see if TCP data has arrived, and if so """
    isCurrentLeader = True
    electionInProgress = False
    def __init__(self, outQ = queue.Queue(), inQ = queue.Queue(),
                 pid = 0, myIP="127.0.0.1", myPort=8888,timeout=10,tickTime=5, **kwargs):
        super().__init__()
        self.outQ = outQ
        self.inQ = inQ
        self.liveQs = queue.Queue()
        self.pid = pid
        self.daemon = True
        self.inMessages = []
        self.myIP = myIP
        self.myPort = myPort
        self.isLeader = True
        self.clIP = "127.0.0.1"
        self.clP = 7777
        self.live = ""
        self.currentTick = 0
        self.timeout = timeout
        self.tickTime = tickTime
        self.reqNum = 0
        self.lock = threading.Lock()
        self.running = True

    def checkData(self):
        if self.inQ.qsize() > 0:
            itm = self.inQ.get()
            print(itm)
            obj = pickle.loads(itm)
            self.inMessages.append(obj)

    def getReqNum(self):
        with self.lock:
            x = self.reqNum
            self.reqNum += 1
        return x

    def ttime(self):    
        self.currentTick += 1
        if self.currentTick % self.timeout == 0:
            self.checkLive()
        self.live = threading.Timer(self.tickTime,self.ttime).start()
        
    def imTheLeaderNow(self):
        self.isCurrentLeader = True
    def gotResponse(self):
        if self.electTimer is not None:
            self.electTimer.cancel()

    def elect(self):
        self.electionInProgress = True
        rq = self.getReqNum()
        self.outQ.put(pickle.dumps(LeaderMessage(self.pid,rq,self.myIP,self.myPort),protocol=pickle.HIGHEST_PROTOCOL))
        self.electTimer = threading.Timer(self.timeout,self.imTheLeaderNow).start()
    
    def liveTimeoutCheck(self):
        timeouts = False
        while self.liveQs.qsize() > 0:
            lq = self.liveQs.get()
            if self.currentTick - lq[0] > self.timeout:
                timeouts = True
            else:
                self.liveQs.put(lq)
                break
        return timeouts
    
    def checkLive(self):
        if not self.isCurrentLeader and self.liveQs.qsize() == 0:
            rq = self.getReqNum()
            qm = QueryMess(self.pid, rq,self.myIP,self.myPort)
            self.outQ.put((pickle.dumps(qm),self.clIP))
            self.liveQs.put((self.currentTick,self.clIP))


    def okResp(self,dip):
        #self.outQ.put(((OkMess(self.myIP),self.clIP),dip))
        rq = self.getReqNum()
        lm = LeaderMessage(self.pid,rq,self.myIP,self.myPort)
        self.outQ.put(pickle.dumps(lm),self.clIP)
        
       
    def dataHandler(self):
        for m in self.inMessages:
            if isinstance(m,QueryMess):
                self.okResp(m.sourceIP)
            elif isinstance(m,OkMess):
                lt = []
                while self.liveQs.qsize() > 0:
                     wt = self.liveQs.get()
                     lt.append(wt)
                for w in lt:
                    if w[1] != m.sourceIP:
                        self.liveQs.put(w)                    
                    
                
            elif isinstance(m,LeaderMessage):
                print("m.pid",m.pid,"self.pid",self.pid)

                if m.pid < self.pid:
                    self.isCurrentLeader = True
                    
                    cr = self.getReqNum()
                    self.outQ.put(pickle.dumps(LeaderMessage(self.pid,cr,self.myIP,self.myPort)))
                    self.clIP = "127.0.0.1"
                    while self.liveQs.qsize() > 0 :
                        x = self.liveQs.get()
                        self.liveQs.task_done()
                else:
                    self.isCurrentLeader = False
                    self.clIP = m.sourceIP
                    self.gotResponse()
        self.inMessages.clear()


    def run(self):
        print("Leader starting!!!")
        self.live = threading.Timer(1,self.ttime)
        self.live.start()
        self.elect()
        while(True):
            time.sleep(1)
            if self.running:
                
                self.checkData()
                self.dataHandler()
                if self.liveTimeoutCheck() :
                    self.elect()

            else:
                if self.live is not None:
                    self.live.cancel()



class fakeServer(object):

    def __init__(self, n = 2, th=True):

        self.outQs =[] 
        self.inQs = []
        self.currentSender = 0
        for i in range(n):
            if th:
                self.outQs.append(queue.Queue())
                self.inQs.append(queue.Queue())
            else:
                self.outQs.append(asyncio.Queue())
                self.inQs.append(asyncio.Queue())

        self.queues = []
        self.n = n
        for i in range(n):
            self.queues.append((self.inQs[i],self.outQs[i]))
        
    def fakeSend(self):
        if self.outQs[self.currentSender].qsize() > 0:
            m = self.outQs[self.currentSender].get()
            ct = 0
            for q in self.inQs:
                if isinstance(m, tuple):
                    v = pickle.loads(m[0])
                else:
                    v = pickle.loads(m)
                pid = 0
                #if isinstance(v,tuple):
                #   pid = v[0].pid
                #else:
                pid = v.pid

                if pid != ct:
                    q.put(pickle.dumps(v))
                ct += 1
        print("sent from id " + str(self.currentSender))
        self.currentSender += 1
        self.currentSender = self.currentSender % self.n

                
def pq(q):
    x = ""
    itms = []
    while q.qsize() > 0:
        itms.append(q.get())

    for i in itms:
        if isinstance(i, tuple):
            d = pickle.loads(i[0])
        else:
            d = pickle.loads(i)
        x = x + d.__str__() + ","
        q.put(i)
    return x

def main():
    
    n = 2
    srvr = fakeServer(n)


    leaders = []
    for n in range(n):
        leaders.append(Leader(myIP="localhost" + str(n),pid=n, inQ=srvr.inQs[n], outQ=srvr.outQs[n]))

    for ldr in leaders:
        ldr.start()

    iz = ""
    while iz != "q":
        iz = input("Continue, or kill/start leader #")
        if iz.isdigit() and int(iz) < len(leaders):
            tn = int(iz)
            if leaders[tn].running.is_set():
                leaders[tn].running.clear()
            else:
                leaders[tn].running.set()


        i = 0
        for inq,outq in srvr.queues:
          print("Srvr q " + str(i) + " is: In:" + pq(inq) + " Out: " + pq(outq))
          i += 1
        
        for leader in leaders:
            if leader.isCurrentLeader:
                print("leader " + str(leader.pid) + " thinks it is leader.")
        srvr.fakeSend()

@asyncio.coroutine
def menu(leaders,srvr,loop): 
    iz = ""
    iz = input("Continue, or kill/start leader #")
    if iz.isdigit() and int(iz) < len(leaders):
        tn = int(iz)
        leaders[tn].running = not leaders[tn].running
        for i in range(len(leaders)):
            if i is not tn:
                leaders[i].discEvent.set()
    i = 0
    for inq,outq in srvr.queues:
        print("Srvr q " + str(i) + " is: In:" + pq(inq) + " Out: " + pq(outq))
        i += 1
    for leader in leaders:
        if leader.isCurrentLeader:
            print("leader " + str(leader.pid) + " thinks it is leader.")
    srvr.fakeSend()   
    yield from asyncio.sleep(2)
    yield from menu(leaders,srvr,loop)
  
def asMain():
    n = 2
    srvr = fakeServer(n)
    
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    loop = asyncio.get_event_loop()
    leaders = []
    tasks = []
    
    for n in range(n):
        leaders.append(LeaderAs(loop,myIP="localhost" + str(n),pid=n, inQ=srvr.inQs[n], outQ=srvr.outQs[n]))
    for l in leaders:
        tasks.append(asyncio.ensure_future(l.run()))
        #asyncio.run_coroutine_threadsafe(l.run,loop)
    #loop.run_until_complete(asyncio.wait(tasks))
    loop.create_task(menu(leaders,srvr,loop))
    loop.run_forever()
    loop.close()
    
        

if __name__ == "__main__":
    #sys.exit(int(main() or 0))
    asMain()



#class LeaderAs(object):
#    isCurrentLeader = True

#    def __init__(self, outQ = queue.Queue(), inQ = queue.Queue(),
#                 pid = 0, myIP="127.0.0.1", myPort=8888, **kwargs):
#        self.outQ = outQ
#        self.inQ = inQ
#        self.liveQs = []
#        self.pid = pid
#        self.daemon = True
#        self.inMessages = []
#        self.myIP = myIP
#        self.myPort = myPort
        
#        self.clIP = "127.0.0.1"
#        self.clP = 7777
#        self.live = ""
#        self.currentTick = 0
#        self.timeout = 10

#    def checkData(self):
#        if self.inQ.qsize() > 0:
#            itm = self.inQ.get()
#            obj = pickle.loads(itm)
#            self.inMessages.append(obj)

#    def ttime(self):
#        print("Tick...")
#        self.currentTick += 1
#        if self.currentTick % 5 == 0:
#            self.checkLive()
#        threading.Timer(1,self.ttime).start()

     
#    def elect(self):
#        self.outQ.put(pickle.dumps(LeaderMessage(self.pid,0,self.myIP,self.myPort),protocol=pickle.HIGHEST_PROTOCOL))

#    def liveTimeoutCheck(self):
#        timeouts = False
#        for lq in self.liveQs:
#            if self.currentTick - lq[0] > self.timeout:
#                timeouts = True
#        return timeouts

#    def checkLive(self):
#        if not self.isCurrentLeader:
#            self.outQ.put(pickle.dumps((QueryMess(self.myIP),self.clIP)))
#            self.liveQs.append((self.currentTick,self.clIP))


#    def okResp(self,dip):
#        self.outQ.put(((OkMess(self.myIP),self.clIP),dip))
        
#    def dataHandler(self):
#        for m in self.inMessages:
#            if isinstance(m,QueryMess):
#                self.okResp(m.sourceIP)
#            elif isinstance(m,LeaderMessage):
#                if m.pid > self.pid:
#                    self.isCurrentLeader = True
#                    self.outQ.put(pickle.dumps(LeaderMessage(self.pid,0,self.myIP,self.myPort)))


#    @asyncio.coroutine
#    def run(self):
#        self.live = threading.Timer(1,self.ttime)
#        self.live.start()
#        self.elect()
#        while(True):
#            self.checkData()
           
#            if self.liveTimeoutCheck():
#                self.elect()
#            yield from asyncio.sleep(1)