import queue
import threading
from MessDef import dePickle

class GCD(threading.Thread):

    def __init__(self,inQ=queue.Queue(), propQ=queue.Queue(), acceptQ=queue.Queue()):
        super().__init__()
        self.inQ = inQ
        self.propQ = propQ
        self.acceptQ = acceptQ


    def run(self):
        while 'pigs' != 'can fly':
            if self.inQ.qsize() > 0:
                print("GCD: Recieved a message... ",end='')
                #You have a message!!
                pickledMessage = self.inQ.get()

                print("Depickling.")

                #Depickle the message
                depickledMessage = dePickle(pickledMessage)


                #What type of message is it?
                    #PROPOSAL, RESULT, PROMISE, ACK -> PROPOSER
                messType = depickledMessage.messType

                if messType == 'PROPOSAL' or messType == 'RESULT' or messType == 'PROMISE' or messType == 'ACK':
                    self.propQ.put(depickledMessage)
                    print("GCD SENT MESSAGE TO PROPOSER")

                     #PREPARE, ACCEPT, COMMIT-> ACCEPTOR
                elif messType == 'PREPARE' or messType == 'ACCEPT' or messType == 'COMMIT':
                    self.acceptQ.put(depickledMessage)
                    print("GCD SENT MESSAGE TO ACCEPTOR")
