import threading
from collections import deque
import time
from benc import *

class InPost:
    def __init__(self, post, delay=0.005, handlers=[], on_fail=None):
        """Post must allow to get requests from OutPost - method get.
        It must always return n FULL requests (for example cant return 1.5 request ) """
        self.inp = deque()
        self.post = post
        self.delay = delay
        self.handlers = {handler.ID:handler.handle for handler in handlers}
        self.on_fail = on_fail
        self.handle_loop = threading.Thread(target=self._handle_loop)
        self.STOP = False
        self.handle_loop.start()

    def read_request(self, data):
        """Requests has this format:
           |1 byte HANDLER ID |  3 bytes REQUEST_LEN | request_len bytes  REQ|
           returns tuple HANDLER_ID (int), REQ, REMAINING_DATA
        """
        ID = ord(data[0])
        LEN = from_bytes(data[1:4])+4
        return ID, data[4:LEN], data[LEN:]

    def dispath_requests(self, data):
        while data:
            try:
                handler_id, req, data = self.read_request(data)
                handler = self.handlers.get(handler_id)
                if handler is None:
                    print 'Invalid handler!'
                threading.Thread(target=handler, args=(req,)).start()
            except:
                print 'Invalid request!', data
                break

    def _handle_loop(self):
        while not self.STOP:
            t = time.time()
            data = ''
            try:
                data = self.post.get()
            except:
                if self.on_fail:
                    try:
                        self.on_fail()
                    except: # we can't fail!
                        pass
            print time.time()-t
            self.dispath_requests(data)



