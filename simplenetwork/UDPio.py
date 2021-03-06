﻿from simplenetwork import serverData
from simplenetwork.serverData import udpPort,udpDests
import socketserver
import socket
import simplenetwork
import threading
import sys
import random
import time
sq = serverData.mainServerQueue

running = True

###UDP


class udpDataHanlder(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        if isinstance(data, tuple):
            data = data[0]
        sq.inUDP.put(data)
        print("Got UDP data")

class thUDPHandler(socketserver.ThreadingMixIn,socketserver.UDPServer):
    pass

sndrRun = True
def udpSendData():
    udest = serverData.udpDests
    port = serverData.udpPort
    while sndrRun:
        if sq.outUDP.qsize() > 0:
            data = sq.outUDP.get(block=True)
            print("UDP: Send Data")
            if isinstance(data, tuple):
                message = data[0]
                destIP =data[1]
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(bytes(message),(destIP,port))
            else:                      
                for host in udest:
                    print("UDP SENDING TO: %s"%host)
                    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                    sock.sendto(bytes(data), (host,port))
        time.sleep(2)
def udpRun():
    UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    UDPSock.bind(("",serverData.udpPort))
    while True:
        data,addr = UDPSock.recvfrom(7777)
        print(data.strip())

def runUDP():
    print("In Main")
    host, port = "",serverData.udpPort
    udpserver = thUDPHandler((host,port),udpDataHanlder)
    udp_thread = threading.Thread(target=udpserver.serve_forever)
    udp_thread.daemon = True
    udp_thread.start()
    sender = threading.Thread(target=udpSendData)
    sender.daemon = True
    sender.start()
    
    return udpserver,sender 
def testUDP():
    
    print("In Main")
    host, port = "127.0.0.1",serverData.udpPort
    udpserver = thUDPHandler((host,port),udpDataHanlder)
    udp_thread = threading.Thread(target=udpserver.serve_forever)
    udp_thread.daemon = True
    udp_thread.start()
    sender = threading.Thread(target=udpSendData)
    sender.daemon = True
    sender.start()
    
    return udpserver,sender 
    
def main():
    testUDP()

if __name__ == "__main__":
    sys.exit(int(main() or 0))
