from simplenetwork import serverData
import asyncio
try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair
sq = serverData.mainServerQueue

### TCP Servers:
clients = []
lostClients = asyncio.Queue()
leaderEvt = None
class TCPServerProtocol(asyncio.Protocol):

    def connection_made(self,transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        clients.append(self)

    def data_received(self, data):
        sq.inTCP.put(data)

    def connection_lost(self, exc):
        print("Connection lost to a process")
        lostClients.put(self)
        clients.remove(self)
        if leaderEvt is not None:
            leaderEvt.set()



##TCP Clients (send data):

@asyncio.coroutine
def sendTCPAll(loop):
    while True:
        
        while sq.outTCP.qsize() > 0:
            print("Sending a message")
            msg = sq.outTCP.get()
            if isinstance(msg, tuple):
                message = msg[0]
                destIP = msg[1]
                destPort = serverData.tcpPort
                yield from threadWriter([destIP,destPort],message,loop)
            else:
                message_dests = serverData.getDests()
           
                message_dests[str(msg.destID)][1].append(msg)
                for dest in message_dests:
                    # print("INDIVID DST:", dest)
                    if len(message_dests[str(dest)]) is 0:
                        pass
                    else:
                        #print(str(message_dests[str(dest)][0]))

                        #reader,writer = yield  from asyncio.open_connection(deststr,                        loop=loop)

                        #

                        # print("DEESSST TEST", dest)
                        for mess in message_dests[str(dest)][1]:
                            yield from threadWriter(message_dests[str(dest)][0],mess,loop)
        yield  from asyncio.sleep(1)
@asyncio.coroutine
def threadWriter(host, message,Loop):
    try:
        reader,writer = yield from asyncio.open_connection(host=host[0],port=int(host[1]),loop=Loop)
        # print("Sending messsssssage:", host[0], host[1])
        writer.write(message.encode())
        yield from writer.drain()
        writer.close()
        print("Message Send Complete")
    except:
        print("Lost connection to a process")
