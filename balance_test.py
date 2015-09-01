from state import state
from math import *

s = state.State()
from motor.motors import Motors
import time
TEST_MOTORS = False # Should be clockwise starting from left top motor (Looking from top of the quad UP = Forward)
m = Motors()
n = 0
while TEST_MOTORS:
    m.set_n(n%4, 200)
    time.sleep(0.8)
    m.set_n(n%4, 0)
    n += 1


def get_th(val):
    K = 3
    if val>0:
        return min(val*K, 100)
    return max(val*K, -100)

def on_updated_state(state):
    # Positive Pitch = Right. Negative Roll = Forward
    yaw, pitch, roll = state.yaw, state.pitch, state.roll
    thr = [250,250,250,250]
    if abs(pitch)>5:
        th = get_th(pitch)
        thr[0] += -th
        thr[1] += th
        thr[2] += th
        thr[3] += -th
    if abs(roll)>5:
        th = get_th(roll)
        thr[0] += -th
        thr[1] += -th
        thr[2] += th
        thr[3] += th
    for n, t in enumerate(thr):
        m.set_n(n, max(0, min(t, 350)))




s.on_updated_state = on_updated_state
s.run()
