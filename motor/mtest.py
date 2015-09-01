from motor import Motor
import time



MOTORS = [Motor(e) for e in xrange(4)]
try:
 for m in MOTORS:
     m.set_throtle(200)
 time.sleep(1000)
finally:
   for m in MOTORS:
      m.set_throttle(0)


