import pickle

class LeadMess(object):

    def __init__(self,messType,senderIP,recipientIP,senderID=-1):
        self.messType = messType
        self.senderIP = senderIP
        self.recipientIP = recipientIP
        self.senderID = senderID


    def pickleMe(self):
        return pickle.dumps(self)

    def depickle(self):
        return pickle.loads(self)