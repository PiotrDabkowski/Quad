from motor import Motor
import time



MOTORS = [Motor(e) for e in xrange(4)]

for m in MOTORS:
    m.set_throtle(100)
    time.sleep(5)
    m.set_throtle(0)
