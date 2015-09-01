from pwm import PWM

_driver = PWM()
CONNECTIONS = [1, 0, 3, 2]

class Motor:
    def __init__(self, channel):
        """Inits the motor at this channel. motor is idle."""
        self._channel = channel
        self._driver = _driver
        self.set_throttle(0)
        


    def set_throttle(self, throttle):
        """thrust must be between 0 and 1000
           Unfortunatelly the resolution is not perfect - driver has only 200 different levels. So increment by more than
           5 in order to see the results"""
        if not 0<=throttle<=1000:
            raise ValueError('Invalid throttle')
        self._driver.set_throttle(self._channel, int(throttle))

        


class Motors:
    def __init__(self):
        self.motors = [Motor(e) for e in CONNECTIONS]
        self._a, self._b, self._c, self._d = self.motors
        self.off()

    def off(self):
        self.set_all(0)

    def set_all(self, throttle):
        for m in self.motors:
            m.set_throttle(throttle)

    def set_0(self, th):  #  Top Left
        self._a.set_throttle(th)

    def set_1(self, th): # Top Right
        self._b.set_throttle(th)

    def set_2(self, th): # Bottom Right
        self._c.set_throttle(th)

    def set_3(self, th): # Bottom Left
        self._d.set_throttle(th)

    def set_n(self, n, th):
        self.motors[n].set_throttle(th)

    def __del__(self):
        for m in self.motors:
           m.set_throttle(0)

