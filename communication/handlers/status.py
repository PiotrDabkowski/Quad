"""Sends current state of the quad in json format.
   Again required paramteres can be set using commander. Default values are set in Quad class."""
import json
import time
from base_handler import InHandler, OutHandler
from collections import deque


def get_stamp():
    '''10s max delay! 0.01s resolution'''
    return int(time.time()*1000)%1000

def from_stamp(stamp):
    '''10s max delay! 0.01s resolution'''
    t = time.time()
    d = int(t*1000)%1000 - stamp
    if d<0:
        d += 1000
    return t - d*0.001


class OutStatus(OutHandler):
    ID = 19
    def __init__(self, quad, send_stamp=True):
        self.quad = quad
        self.send_stamp = send_stamp


    def send_status(self):
        """Sends current state of the quad"""
        status = self.quad._get_status()
        if self.send_stamp:
            status['t'] = get_stamp()
        self.send(json.dumps(status, separators=(',', ':')))  # this is our request


class InStatus(InHandler):
    ID = 19
    def __init__(self, gui):
        self.status_seq = deque()
        self.gui = gui

    def on_status_update(self, status):
        pass

    def handle(self, req):
        status = json.loads(req)
        stamp = status.get('t')
        if stamp is not None:
            status['t'] = from_stamp(stamp)
        print status
        print time.time()
        self.status_seq.append(status)
        self.on_status_update(status)

