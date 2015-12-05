import socketserver
import asyncio
import socket
import threading
import simplenetwork.serverData
from simplenetwork.serverData import udpDests,udpPort,myIP
from simplenetwork import TCPio, UDPio
from simplenetwork.serverData import mainServerQueue as sq
try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair


tcpPort = simplenetwork.serverData.tcpPort
udpPort = simplenetwork.serverData.udpPort


running = False
threads = []
tcpServer = ""
coro = ""

def startupThreadedServers():
    print("Starting up network stack")
    #udpServer = UDPio.thUDPHandler((myIP, udpPort),UDPio.thUDPHandler)
    #udpServer = server = socketserver.ThreadingUDPServer()
    #ip,port = udpServer.server_address
    #threads.append( threading.Thread(target=udpServer.serve_forever))

    srvr, sender = UDPio.runUDP()
    running = True
    simplenetwork.UDPio.running = True
    simplenetwork.UDPio.sndrRun = True
    threads.append(srvr)
    threads.append(sender)
    print("threads init")


def startupServers(hostFile):
    startupThreadedServers()
    if hostFile is not None:
        procIPs = simplenetwork.serverData.getDests(hostFile)
        simplenetwork.serverData.tcpDests = procIPs
        for pid in procIPs:
            simplenetwork.serverData.udpDests.append(pid)

    #loop = asyncio.get_event_loop()
   
    #coro = loop.create_connection(TCPio.TCPServerProtocol,local_addr=("127.0.0.1",simplenetwork.serverData.tcpPort))
    #rsock = socket.socket(family=AF_INET)
    
    #coro = loop.create_server(TCPio.TCPServerShort,host="127.0.0.1",port=simplenetwork.serverData.tcpPort,reuse_address=True)

    server = TCPio.thTCPServer(("localhost",simplenetwork.serverData.tcpPort), TCPio.thTCPServerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("TCP Finished")
    return server

def startSender():
    #loop = asyncio.get_event_loop()
    #coro = asyncio.ensure_future(TCPio.sendTCPAll(loop))
    #loop.run_in_executor(executor=None,func=TCPio.sendTCPAll(loop))
    
    #loop.run_until_complete(coro)
    x = threading.Thread(target=TCPio.tcpSendTh)
    #x = threading.Thread(target=TCPio.tcpSendThPersist)
    x.start()
    return x





@asyncio.coroutine
def closeServers():
    tcpServer.close()
    running = False
    loop = asyncio.get_event_loop()
    loop.close()
    loop.run_until_complete(tcpServer.wait_closed())

if __name__ == '__main__':
    if not running:
        udpDests.append(("127.0.0.1",7777))
        startupServers()
        try:
            while  True:
                data = input("Press enter to send:")
                sq.outUDP.put(data)
        except:
            print("closing")