from PIL import Image
import StringIO
import time
from benc import *

class CamI:
    ID = 11
    def __init__(self, display=None, delay=2.0):
        self.display = display
        self.delay = delay

    def handle(self, data):
       print 'Handling...'
       show = from_bytes(data[:6])/1000.0 + self.delay
       im = Image.open(StringIO.StringIO(data[6:]))
       if time.time()>show:
           print 'FRAME LATE!!!!'
       while time.time()<show:
          time.sleep(0.005)
       self.display.change_frame(im)

