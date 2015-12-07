import threading




class Representative(threading.Thread):


    def __init__(self, pid=1, N=1, curLeaderIP='127.0.0.1', myIP='127.0.0.1',timeout=10):
        self.pid
        self.N
        self.curLeaderIP
        self.myIP
        self.iAmLeader = True
        self.timeout = timeout



    def election(self):
        pass
