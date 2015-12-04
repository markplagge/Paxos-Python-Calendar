import queue
import threading

class GCD(threading.Thread):

    def __init__(self,inQ=queue.Queue(), propQ=queue.Queue(), acceptQ=queue.Queue()):
        self.inQ = inQ
        self.propQ = propQ
        self.acceptQ = acceptQ


    def run(self):
        while 'pigs' != 'can fly':
            if self.inQ.qsize() > 0:
                #You have a message!!
                pickledMessage = self.inQ.get()

                #Depickle the message
                depickledMessage = pickledMessage.dePickle()

                #What type of message is it?
                    #PROPOSAL, RESULT, PROMISE, ACK -> PROPOSER
                messType = depickledMessage.messType

                if messType == 'PROPOSAL' or messType == 'RESULT' or messType == 'PROMISE' or messType == 'ACK':
                    self.propQ.put(depickledMessage)

                     #PREPARE, ACCEPT, COMMIT-> ACCEPTOR
                elif messType == 'PREPARE' or messType == 'ACCEPT' or messType == 'COMMIT':
                    self.acceptQ.put(depickledMessage)
