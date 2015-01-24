from picamera import PiCamera
from StringIO import StringIO
KB = 1000

class CamO:
    ID = 11
    def __init__(self, resolution=(450, 300)):
        self.cam = PiCamera()
        self.set_resolution(resolution)

    def set_resolution(self, resolution):
        self.resolution = resolution
        self.cam.resolution = resolution

    def take_img(self):
        """Quality is OK we dont have to change it"""
        img = StringIO()
        print 'Taking image...'
        self.cam.capture(img, format='jpeg', use_video_port=True)
        print 'Took image!'
        return img.getvalue()
