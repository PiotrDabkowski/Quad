"""Sends message to be displayed on command window on PC."""
from base_handler import OutHandler, InHandler



class OutInfo(OutHandler):
    ID = 9
    def send(self, message):
        if self.out:
            self.out.add(message, self.ID)


class InInfo(InHandler):
    ID = 9
    def __init__(self, gui):
        self.gui = gui

    def handle(self, req):
        print req
        #self.gui.log(req)
