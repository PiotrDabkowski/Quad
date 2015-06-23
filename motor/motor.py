from pwm import PWM
_driver = PWM()


class Motor:
    def __init__(self, channel):
        """Inits the motor at this channel. motor is idle."""
        self._channel = channel
        self.set_throtle(0)

    def set_throtle(self, throttle):
        """thrust must be between 0 and 1000
           Unfortunatelly the resolution is not perfect - driver has only 200 different levels. So increment by more than
           5 in order to see the results"""
        if not 0<=throttle<=1000:
            raise ValueError('Invalid throttle')
        if throttle>700:
            raise ValueError('Not safe yet :D')
        _driver.set_throttle(self._channel, int(throttle))

    def __del__(self):
        _driver.set_throttle(self._channel, 0)



