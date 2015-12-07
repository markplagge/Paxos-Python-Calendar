import pickle

class LeadMess(object):

    def __init__(self,messType,senderIP,recipientIP):
        self.messType = messType
        self.senderIP = senderIP
        self.recipientIP = recipientIP


    def pickleMe(self):
        return pickle.dumps(self)

    def depickle(self):
        return pickle.loads(self)