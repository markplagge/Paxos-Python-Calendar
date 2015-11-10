from simplenetwork import serverData
from simplenetwork.serverData import udpPort,udpDests
import socketserver
import socket
import simplenetwork
sq = serverData.mainServerQueue

running = True

###UDP


class udpDataHanlder(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        sq.outUDP.put(data.format())
        print("Got data: " + data.decode())

class thUDPHandler(socketserver.ThreadingMixIn,socketserver.UDPServer):
    pass

def udpSendData():
    while running:
        if sq.outUDP.qsize() > 0:
            data = sq.outUDP.get(block=True)
            for host in udpDests:

                #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                sock.sendto(bytes(data.encode()), host)
def udpRun():
    UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    UDPSock.bind(("",serverData.udpPort))
    while True:
        data,addr = UDPSock.recvfrom(5098)
        print(data.strip())
