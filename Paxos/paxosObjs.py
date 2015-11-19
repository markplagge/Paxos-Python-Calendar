import collections
import threading
class pMessenger(object):
    """Represents the messengers"""
    def send_prepare(self, proposal_id):
        pass
    
    def send_promise(self, proposer_uid, proposal_id, previous_id, accepted_value):
        pass
    def send_accept(self, proposal_id, proposal_value):
        pass

    def send_accepted(self, proposal_id, accepted_value):
        pass

    def on_resolution(self, proposal_id, value):
        pass

class pLearner(threading.Thread):
    """Represents the learner object -saves log to disk"""
    pass

class pAcceptor(threading.Thread):
    """The paxos acceptor"""
    pass
