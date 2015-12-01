from simplenetwork import serverData
import socket
import socketserver
import threading
import multiprocessing
import json
import time
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
## Threaded TCP Server
def server():

    sct = socket.socket()
    sct.bind("localhost", serverData.tcpPort)



class thTCPServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        
        data = self.request.recv(10000).decode()
        cur_thread = threading.current_thread()
        serverData.mainServerQueue.inTCP.put(data)
        print("TCP Rcvd data: " + str(data))
class thTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass




@asyncio.coroutine
def TCPServerShort(reader,writer):
    data = yield from reader.read(100000)
    message = data.decode()
    print("Recevd tcp data")
    sq.inTCP.put(message)
    
class TCPServerProtocol(asyncio.Protocol):

    def connection_made(self,transport):
        print("TCP CONNECTION MADE")
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        #clients.append(self)

    def data_received(self, data):
        print("TCP Rec. data")
        sq.inTCP.put(data.decode())

    def connection_lost(self, exc):
        print("Connection lost to a process")
        #lostClients.put(self)
        #clients.remove(self)
        if leaderEvt is not None:
            leaderEvt.set()
@asyncio.coroutine
def tcpServerAsync(reader, writer):
    data = yield from reader.read(9048)
    message = data.decode()
    print("TCP MEssage RCVD")
    sq.inTCP.put(message)


class tcpClientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.transport = None
        self.loop = loop
        self.queue = serverData.mainServerQueue.outTCP
        self._ready = asyncio.Event()
        asyncio.async(self._send_messages())

    @asyncio.coroutine
    def _send_messages(self):
        yield from self._ready.wait()
        print("client is ready")
        while True:
            if(self.queue.qsize() > 0):
                data =self.queue.get()
                self.transport.write(data.encode('utf-8'))
                print('message sendt: {!r}'.format(data))
            else:
                yield from asyncio.sleep(2)

    def connection_made(self,transport):
        self.transport = transport
        print("Connection made")
        self._ready.set()

    @asyncio.coroutine
    def send_message(self, data):
        """ Feed a message to the sender coroutine. """
        self.queue.put(data)

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

@asyncio.coroutine
def feed_messages(protocol):
    """ An example function that sends the same message repeatedly. """
    message = json.dumps({'type': 'subscribe', 'channel': 'sensor'},
                         separators=(',', ':'))
    while True:
        yield from protocol.send_message(message)
        yield from asyncio.sleep(1)

def main():
    message = json.dumps({'type': 'subscribe', 'channel': 'sensor'},
                         separators=(',', ':'))

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(lambda: tcpClientProtocol(loop),
                                  '127.0.0.1', serverData.tcpPort)
    _, proto = loop.run_until_complete(coro)
    asyncio.async(feed_messages(proto))  # Or asyncio.ensure_future if using 3.4.3+
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Closing connection')
    loop.close()
##TCP Clients (send data):
def lostTCPConnection(data):
    print("LOST A TCP CONNECTION TO SERVER")
    sq.outTCP.put(data)
    
def tcpSendTh():
    if(sq.outTCP.qsize() > 0):
        msg = sq.outTCP.get()
        if isinstance(msg,tuple):
            dest = msg[1]
            data = msg[0]
            try:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                sock.connect((dest,serverData.tcpPort))
                sock.send(data.encode())
            except:
                lostTCPConnection(msg)
        else:
            ##broadcast
            for dest in serverData.tcpDests:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    sock.connect((dest,serverData.tcpPort))
                    sock.send(msg.encode())
                except:
                    lostTCPConnection(msg)
    threading.Timer(1.5,tcpSendTh).start()
def sender(sock, message):
    try:
        sock.send(message.encode())
    except:
        lostTCPConnection(message)

def tcpSendThPersist():
    clients = {}
    for dest in serverData.tcpDests:
        sock = socket.socket()
        sock.connect((dest,serverData.tcpPort))
        clients[dest] = sock

    while True:
        if(sq.outTCP.qsize() > 0):
            msg = sq.outTCP.get()
            if isinstance(msg,tuple):
                dest = msg[1]
                data = msg[0]
                try:
                    sock = clients[dest]

                    sock.send(data.encode())
                except:
                    lostTCPConnection(data)
            else:
                for sock in clients:
                    threading.Thread(target=sender,args=(sock,msg))






@asyncio.coroutine
def sendTCPAll(loop):
    while True:
        
        while sq.outTCP.qsize() > 0:
            print("Sending a message")
            msg = sq.outTCP.get()
            destPort = serverData.tcpPort
            if isinstance(msg, tuple):
                message = msg[0]
                destIP = msg[1]
                
                yield from threadWriter([destIP,destPort],message,loop)
            else:
                message_dests = serverData.tcpDests

                for dest in message_dests:
                    # print("INDIVID DST:", dest)        
                    yield from threadWriter((dest,destPort),msg,loop)
        yield  from asyncio.sleep(2)
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
