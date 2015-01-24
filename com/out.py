import threading
from collections import deque
import time
from benc import *

class OutPost:
    def __init__(self, post, cam=None, delay=0.005, on_fail=None):
        """Post must allow to send any number of bytes to InPost - method send.
           post.send('string') """
        self.out = deque()
        self.post = post
        self.delay = delay
        self.on_fail = on_fail
        self.cam = cam
        self.handle_loop = threading.Thread(target=self._handle_loop)
        self.STOP = False
        self.add('lol', 30)
        self.handle_loop.start()

    def _handle_loop(self):
        last_photo = None
        print 'here'
        while not self.STOP:
            data = ''
            while not self.out:
                time.sleep(self.delay)
            while self.out:
                 data += self.out.popleft()
            try:
                print 'Trying to send'
                self.post.send(data)
                print 'sent!'
            except:
                print 'failed to send'
                if self.on_fail:
                    try:
                        self.on_fail()
                    except: # we can't fail!
                        pass
            if self.cam:
                if last_photo:
                    #adjust camera settings...
                    pass
                print 'taking photo'
                self.add(self.cam.take_img(), self.cam.ID)
                print 'added photo!'

    def add(self, data, handler_id):
        print 'adding'
        han = chr(handler_id)
        dl8 = to_bytes(len(data), 3)
        self.out.append(han + dl8 + data)
        print 'added'