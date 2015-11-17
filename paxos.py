import asyncio
import leader
import simplenetwork
import Paxos
import pCalendar
import sys




class paxos(object):
    """this class contains a leader, a server, calendar/log objects, and
       links them together.
    """

    def __init__(self,loop, myIP="127.0.0.1", myTCPPort=8888, myUDPPort=7777, myUID=0,
                 hostFile=None):
        self.file=hostFile
        self.loop = loop
        self.myIP = myIP
        self.tcpPort = myTCPPort
        self.udpPort = myUDPPort
        self.uid = myUID
        
        self.tcpOut = simplenetwork.serverData.mainServerQueue.outTCP
        self.tcpIn = simplenetwork.serverData.mainServerQueue.inTCP
        self.udpOut = simplenetwork.serverData.mainServerQueue.outUDP
        self.udpIn = simplenetwork.serverData.mainServerQueue.inUDP
        self.leader = leader.MLeader(loop,self.tcpOut,self.tcpIn,myUID,
                                     myIP,myTCPPort)

        #set up server
        loop = asyncio.get_event_loop()
        coro = loop.create_server(simplenetwork.TCPio.TCPServerProtocol, port=myTCPPort)
        simplenetwork.TCPio.leaderEvt = self.leader.discEvent

    def run(self):
        simplenetwork.Servers.startupThreadedServers()



def main():
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

    loop = asyncio.get_event_loop()

    main = paxos(loop)

if __name__ == "__main__":
    sys.exit(int(main() or 0))