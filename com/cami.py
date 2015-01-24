from PIL import Image
import StringIO

class CamI:
    ID = 11
    def __init__(self, display=None):
        self.display = display

    def handle(self, data):
        print 'Here'
        self.display.change_frame(Image.open(StringIO.StringIO(data)))

