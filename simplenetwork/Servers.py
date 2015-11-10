import socketserver
import asyncio
import socket
import threading
import simplenetwork.serverData
from simplenetwork.serverData import tcpDests,tcpPort,udpDests,udpPort,myIP
from simplenetwork import TCPio, UDPio
from simplenetwork.serverData import mainServerQueue as sq



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
    threads.append(threading.Thread(target=UDPio.udpRun))
    threads.append( threading.Thread(target=UDPio.udpSendData))
    running = True
    for t in threads:
        assert(isinstance(t, threading.Thread))
        t.start()
    simplenetwork.UDPio.running = True
    print("threads init")


def startupServers():
    startupThreadedServers()
    loop = asyncio.get_event_loop()
    coro = loop.create_server(TCPio.TCPServerProtocol, port=tcpPort)
    return coro





def runServer():
    loop = asyncio.get_event_loop()
    tcpServer = loop.run_until_complete(coro)

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