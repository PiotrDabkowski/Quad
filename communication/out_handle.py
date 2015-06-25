from collections import deque
import time
from benc import *

class OutPost:
    def __init__(self, post, handlers=[]):
        """Post must allow to send any number of bytes to InPost - method send.
           post.send('string') """
        self.out = deque()
        self.post = post
        self.STOP = False
        self.handlers = handlers
        for handler in handlers:
            handler.set_post(self)


    def on_fail(self):
        """called on error in post request"""
        pass

    def _handle_loop(self):
        while not self.STOP:
            data = ''
            while not self.out:
                time.sleep(0.007)
            while self.out:
                 data += self.out.popleft()
            try:
                self.post.send(data)
            except:
                if self.on_fail:
                    try:
                        self.on_fail()
                    except: # we can't fail!
                        pass

    def add(self, data, handler_id):
        han = chr(handler_id)
        dl8 = to_bytes(len(data), 3)
        self.out.append(han + dl8 + data)