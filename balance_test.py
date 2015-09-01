from state import state
from math import *
import time

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

# Outper Loop
#
PITCH_GAIN = 2
ROLL_GAIN = 2
YAW_GAIN = 2


# Inner Loop
# pitch_v and roll_v PID params <3 Bless them
P = 1.5
I = 0.5
D = 0.05

# yaw_v PID params
P_Y = 1
I_Y = 0.3
D_Y = 0.03
LAST = time.time()

class PID:
    def __init__(self, T=0.025, P=P, I=I, D=D):
        self.T = T
        self.out = 0
        self.last_e = 0
        self.all_e = 0
        self.P, self.I, self.D = P, I, D

    def get_out(self, e):
        self.all_e += self.T * e
        d = (e-self.last_e)/self.T
        self.last_e = e
        return P*e + self.D*d + self.I*self.all_e



roll_v_pid = PID(P=P, I=I, D=D)
pitch_v_pid = PID(P=P, I=I, D=D)
yaw_v_pid = PID(P=P_Y, I=I_Y, D=D_Y)

HH = 375
TH_LIMIT = 700

def on_updated_state(state):
    global LAST
    tt = time.time()
    print tt-LAST
    LAST = tt
    # Positive Pitch = Right. Negative Roll = Forward, Positive Yaw= Left
    yaw, pitch, roll = state.yaw, state.pitch, state.roll
    yaw_v, pitch_v, roll_v = state.yaw_v, state.pitch_v, state.roll_v
    thr = [HH,HH,HH,HH]


    # Now, better don't get it wrong :)

    # OUTER LOOP

    # A_VEL = (desired_angle - current_angle) * GAIN
    # It will be exponential function (hopefully decreasing)
    # For balance testing we want 0 pitch, 0 roll and hold yaw.
    req_pitch_v = (0 - pitch) * PITCH_GAIN
    req_roll_v = (0 - roll) * ROLL_GAIN
    req_yaw_v = (yaw - yaw) * YAW_GAIN


    # INNER LOOP


    # Pitch - High pitch counteracted with High th
    th = pitch_v_pid.get_out(pitch_v - req_pitch_v)
    thr[0] -= th
    thr[1] += th
    thr[2] += th
    thr[3] -= th
    # Roll - High roll counteracted with High th
    th = roll_v_pid.get_out(roll_v - req_roll_v)
    thr[0] -= th
    thr[1] -= th
    thr[2] += th
    thr[3] += th

    # Yaw - Again high yaw counteracted with High th. Do not do that now...
    th = yaw_v_pid.get_out(yaw_v - req_yaw_v) # < MAKE SURE THIS IS 0 BEFORE CHECKING ANGLES!
    thr[0] -= th
    thr[1] += th
    thr[2] -= th
    thr[3] += th
    print thr

    if abs(roll)>30 or abs(pitch)>30:
        print 'DANGER!', roll, pitch
        m.set_all(0)
        raise
    for n, t in enumerate(thr):
        if t>TH_LIMIT:
            print 'SATURATED!'
            #m.set_all(0)
            #raise
        m.set_n(n, max(0, min(t, TH_LIMIT)))

def on_dead(state):
    print 'I am dead :( '
    m.set_all(0) # turn off the motors!


s.on_updated_state = on_updated_state
s.on_dead = on_dead
s.run()
