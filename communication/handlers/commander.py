"""Implements basic quad commands using top level quad object"""
from base_handler import OutHandler, InHandler

class OutCommander(OutHandler):
    ID = 7
    def __init__(self):
        pass

    def command(self, code):
        """You can use all attributes of quad object:
           quad.hover();
           quad.motors.off();
           etc..."""
        self.send(str(code))  # this is our request


class InCommander(InHandler):
    ID = 7
    def __init__(self, quad):
        self.quad = quad

    def handle(self, req):
        quad = self.quad
        try:
            exec req in locals()
        except:
            pass

