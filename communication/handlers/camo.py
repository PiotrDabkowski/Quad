from picamera import PiCamera
from StringIO import StringIO
import time
import threading
from benc import *
KB = 1000

class CamO:
    ID = 11
    def __init__(self, out, resolution=(300, 200)):
        self.cam = PiCamera()
        self.set_resolution(resolution)
        self.out = out
        self.STOP = False

    def set_resolution(self, resolution):
        self.resolution = resolution
        self.cam.resolution = resolution

    def take_img(self):
        """Quality is OK we dont have to change it"""
        img = StringIO()
        t = time.time()
        self.cam.capture(img, format='jpeg', use_video_port=True)
        stamp = to_bytes(int((time.time()+t)*500), 6)
        return stamp + img.getvalue()

    def start(self):
        self.cam_loop = threading.Thread(target=self._camera_loop)
        self.cam_loop.start()

    def _camera_loop(self):
        rest = 0.1
        while not self.STOP:
            time.sleep(rest)
            self.out.add(self.take_img(), self.ID)
            if len(self.out.out)>(1/rest):
                rest*=1.05
            else:
                rest*=0.95



