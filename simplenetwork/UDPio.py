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

class thUDPHandler(socketserver.ThreadingMixIn,socketserver.UDPServer):
    pass

def udpSendData():
    while running:
        if sq.outUDP.qsize() > 0:
            for host in udpDests:

                sock = socket.socket(socket.AF, socket.SOCK_DGRAM)
                sock.connect((host,udpPort))
                try:
                    sock.sendall(sq.outUDP.get().encode())
                finally:
                    sock.close()