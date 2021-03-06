﻿import threading
import queue
#import multiprocessing
#import multiprocessing as threading
#from multiprocessing import queues as queue

import sys

import pickle
import asyncio
import time
# from twisted.internet import task
# from twisted.trial import unittest

class LeaderSuper(object):
    def __init__(self, pid,num,ip,port,type):
        self.pid = pid
        self.reqNum = num
        self.sourceIP = ip
        self.sourcePort = port
        self.type=type
        
        

    def __str__(self):
        return "Message from pid " + str(self.pid) + ", IP: " + str(self.sourceIP)

class LeaderMessage(LeaderSuper):
    def __init__(self, pid,num,ip,port):

        super(LeaderMessage, self).__init__(pid,num,ip,port,"LEADER")
    


class PingMessage(LeaderSuper):
    def __init__(self, pid,num,ip,port):

        super(PingMessage, self).__init__(pid,num,ip,port,"LEADER")
        self.type = "PING"
    def __str__(self):
        return "Ping Msg from " + str(self.pid)

class OkMess(LeaderSuper):
    def __init__(self, pid,num,ip,port):
        super(OkMess, self).__init__(pid,num,ip,port,"LEADER")
        self.type="OK"


class AliveMessage(LeaderSuper):
    def __init__(self, pid,num,ip,port):
        super(AliveMessage, self).__init__(pid,num,ip,port,"LEADER")
        self.type="ALIVE"







class Leader(threading.Thread):
#class Leader(multiprocessing.process):

    """Leader represents the leadership role in the program. It
    will poll other servers and ask them for information. It also
    checks to see if TCP data has arrived, and if so """

    def __init__(self, clock=None, transport=None, service=None, outQ = queue.Queue(),
                 inQ = queue.Queue(),
                 pid = 0, myIP="127.0.0.1",
                 myPort=8888, otherPIDs = [], otherIPs = [],
                 timeout=1,tickTime=1, **kwargs):
        super().__init__()

        self.s = "DOWN"
        self.c = 0
        self.h = None
        self.d = 0
        self.known = []
        self.clock = clock
        self.transport = transport
        self.service = service
        self.otherIPs = otherIPs
        self.otherPIDs = otherPIDs
        self.PPIDs = {}
        i = 0
        for pid in otherPIDs:
            self.PPIDs[str(pid)] = otherIPs[i]
            i += 1

        self.outQ = outQ
        self.inQ = inQ
        self.liveQs = queue.Queue()
        self.pid = int(pid)
        self.daemon = True
        self.inMessages = []
        self.myIP = myIP
        self.myPort = myPort
        self.isCurrentLeader = False
        self.clIP = "127.0.0.1"
        # self.clP = 7777
        self.live = ""
        self.currentTick = 0
        self.timeout = timeout
        self.tickTime = tickTime
        self.reqNum = 0
        self.lock = threading.Lock()
        self.running = True
        self.electionInProgress = False


        ##query messages go out for ping
        ##alive messages come back for ping alive

        #election and ok messages are classic bully leader messages.

        self.queryMessages = []
        self.electionMessages = []
        self.okMessages = []
        self.aliveMessages = []

        # highestIP = self.higherPID_IPS[str(len(self.otherPIDs)-1)]
    @property
    def okMess(self):
        return OkMess(self.pid,self.pid,self.myIP,self.myPort)
    @property
    def electionMsg(self):
        return LeaderMessage(self.pid,self.pid,self.myIP,self.myPort)
    @property
    def pngMess(self):
        return PingMessage(self.pid,self.pid,self.myIP,self.myPort)
    @property
    def aliveMsg(self):
        return AliveMessage(self.pid, self.pid, self.myIP, self.myPort)
    @property
    def ldrMesg(self):
        return LeaderMessage(self.pid, self.pid, self.myIP, self.myPort)




    def ping_leader(self):
        """periodically checks on the leader"""
        #if not self.isCurrentLeader:
        pMessage = self.pngMess #PingMessage(self.pid,self.pid,self.myIP,self.myPort)
        #    self.outQ.put((pickle.dumps(pMessage),self.clIP))
        #time.sleep(self.timeout)
        return self.tcpSendTh(pickle.dumps(pMessage))

    def send_ok(self,m):
        okm = self.okMess
        #self.outQ.put((pickle.dumps(okm),m.sourceIP))
        self.tcpSendTh((pickle.dumps(okm), m.sourceIP))

    def send_election_m(self):
        for pid in self.PPIDs:
            if int(pid) > int(self.pid):
                self.tcpSendTh((pickle.dumps(self.okMess),self.PPIDs[pid]))



    def imTheLeaderNow(self):
        self.isCurrentLeader = True
    def gotResponse(self):
        if self.electTimer is not None:
            self.electTimer.cancel()
    def elect(self):
        self.electionInProgress = True
        self.send_election_m()

    @property
    def higherPID_IPS(self):
        highers = {}
        i = 0
        for pid in self.otherPIDs:
            if int(self.pid) < int(pid):
                highers[str(pid)] = self.otherIPs[i]
            i += 1


            print("***** HIGHERS ARE ***" + str(highers))
            return highers
    def tcpSendTh(self, message):
        import socket
        import simplenetwork

        msg = message
        print("TCP Data sending is  " + str(msg))
        if isinstance(msg,tuple):
            destv = msg[1]
            data = msg[0]

            s = str(destv)
            destv = s.rstrip("\\'")
            destv = destv.replace("\\'","")
            destv = destv.replace("\\\\","")

            try:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.settimeout(2)

                sock.connect((destv,simplenetwork.serverData.tcpPort))
                sock.send(data)
            except:
                print(" error in single")
                return False
            finally:
                sock.close()
        else:
                ##broadcast
            for dest in simplenetwork.serverData.tcpDests:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    sock.connect((simplenetwork.tcpDests[dest],simplenetwork.tcpPort))
                    sock.send(msg)
                except:
                    print("error in bcast")
                    return False
                finally:
                    sock.close()
        return True




    def leader_running(self):
        """ once started up, ping the leader until he goes down, then nominate
        ourselves as a leader. If we get a leadership message from someone below us,
        run the election. If we get a leadership message from soneone ubove us,
        set that to leader"""

        if not self.isCurrentLeader:
            print("Not the leader - ping send")
            gotPingResp = self.ping_leader() # blocks for the timeout time
            time.sleep(self.timeout)

            if not gotPingResp:
                print("No response detected from leader, starting election.")
                if not self.electionInProgress and not gotPingResp:
                    self.election_new()
        else:
            self.data_handler_new()
            for m in self.okMessages:
                self.send_ok(m)
        self.okMessages = []




        self.data_handler_new() # handles all messages

        for m in self.electionMessages:
            if int(m.pid) > self.pid: #They are the leader
                self.clIP = m.sourceIP
                self.isCurrentLeader = False
            else: # m.pid < self.pid:
                #self.election_new()
                self.send_ok(m)
                self.election_new()

        self.electionMessages = []

        time.sleep(self.timeout)
    def election_new(self):
        self.elect()
        while self.electionInProgress:
                gotOK = False
                self.data_handler_new()
                higherps = self.higherPID_IPS
                time.sleep(self.timeout)
                lowestRC = -1
                newLdr = None
                if len(self.okMessages) > 0 :
                    self.electionInProgress = False
                    time.sleep(self.timeout) ## Wait a bit, then we will get election results.
                    self.data_handler_new()

                    break
                else:
                    #we did not get an ok at all, we are now the leader:
                    self.isCurrentLeader = True
                    self.electionInProgress = False
                    self.clIP = self.myIP
                    self.no_leader()
        self.okMessages = []
    def no_leader(self):
        for ip in self.otherIPs:
            pickledMess = pickle.dumps(self.ldrMesg)
            if self.myIP is not ip:
                self.outQ.put((pickledMess,ip))
        self.electionMessages =[]

    
                           
    def leader_startup(self):

       self.isCurrentLeader = False
       self.election_new()






    ## v = get_messages(self)
    ## for m in v:
    ##  if isinstance(m, okMessage):
    ##
    def data_handler_new(self):
        time.sleep(self.timeout)
        while self.inQ.qsize() > 0:
            self.inMessages.append(pickle.loads(self.inQ.get()))
        for m in self.inMessages:
            if m.type == "PING":
                self.queryMessages.append(m)
            elif m.type == "OK":
                self.okMessages.append(m)
            elif m.type == "LEADER":
                self.electionMessages.append(m)
            elif m.type == "ALIVE":
                self.aliveMessages.append(m)
            else:
                print("DATA HANDLER GOT INVALID MSG")



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
            qm = PingMessage(self.pid, rq,self.myIP,self.myPort)
            self.outQ.put((pickle.dumps(qm),self.clIP))
            self.liveQs.put((self.currentTick,self.clIP))


    def okResp(self,dip):
        #self.outQ.put(((OkMess(self.myIP),self.clIP),dip))
        rq = self.getReqNum()
        lm = LeaderMessage(self.pid,rq,self.myIP,self.myPort)
        self.outQ.put(pickle.dumps(lm),self.clIP)


    def dataHandler(self):
        for m in self.inMessages:
            if isinstance(m,PingMessage):
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
                    self.clIP = self.myIP
                    while self.liveQs.qsize() > 0 :
                        x = self.liveQs.get()
                        self.liveQs.task_done()
                else:
                    self.isCurrentLeader = False
                    self.clIP = m.sourceIP
                    self.gotResponse()
        self.inMessages.clear()
    master_id =None
    def join(self, node_id):
        self.transport.send(node_id, 'hello', self.pid)
        self.known.append(node_id)

    def leave(self, node_id):
        self.known.remove(node_id)
        if self.master_id == node_id:
            self._start_election()
    # def _proclaim(self):
    #     for nid in self.known:
    #         self.transport.send(node_id, 'leader', self.this_id)
    #     self.state = 'leader'
    #     self.master_id = self.this_id
    #     self.service.setUp()

    # def _restart_election(self):
    #     self.callID =None
    #     self.election = 0
    #     self._start_election()

    def shot_down(self,node_id):
        assert node_id > self.this_id
        if self.callID is not None:
            self.callID.cancel
            self.callID = None

        self.election = 0

        if self.state == 'leader':
            self.service.tearDown()
        self.state = 'waiting'
        self.callID = self.clock.callLAter(5,self._restart_election)

    def leader(self, node_id):
        """
        A node proclaimed that it is the new leader.
        """
        assert node_id > self.this_id
        if self.callID is not None:
            self.callID.cancel()
            self.callID = None
        self.election = 0
        self.master_id = node_id
        if self.state == 'leader':
            self.service.tearDown()
        self.state = 'slave'

    def _start_election(self):
        """
        start an election
        """
        if not self.election:
            for node_id in self.known:
                if node_id > self.this_id:
                    self.transport.send(node_id, 'elect', self.this_id)
            self.election = 1
            self.callID = self.clock.callLater(5, self._proclaim)

    def _elect(self, node_id):
        """
        Received an "ELECT" message from C{node_id}.
        """
        if node_id < self.this_id:
            self.transport.send(node_id, 'shoot-down')
        self._start_election()
    def run(self):
        print("Leader starting!!!")
        time.sleep(10)
        self.election_new()
        while (self.running):
            self.leader_running()
        #self.live = threading.Timer(1,self.ttime)
        #self.live.start()
        
        



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
