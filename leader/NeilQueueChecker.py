import threading

class QueueChecker(threading.Thread):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue


    def run(self):
        while True:
            if self.queue.qsize() > 0:
                pass
                # print(self.queue.qsize())