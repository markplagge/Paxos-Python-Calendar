import queue
import numpy
class serverData(object):
    def __init__(self):
        self.outTCP = queue.Queue()
        self.inTCP = queue.Queue()
        self.outUDP = queue.Queue()
        self.inUDP = queue.Queue()

mainServerQueue = serverData()

tcpDests= {}
udpDests= {}

udpPort = 7777
tcpPort = 8888

myIP = "127.0.0.1"

def getDests():
    hosts = numpy.loadtxt("hosts.info",dtype='S20', delimiter=",")

    ##OK, how do we know what UUID goes to what server?
    #I'm going to assume that the UUID in a message contains the IP:PORT in a tuple for this.
    message_dests = {}
    for host in hosts:
        # print("Host is ", host.astype(str))
        message_dests[host[0].astype(str)] = ((
                                                  str(host[1].astype(str)).strip(),
                                                  str(host[2].astype(str)).strip()),[])
    return message_dests