from motor import Motor

class Motors:
    def __init__(self):
        self.motors = [Motor(e) for e in xrange(4)]
        self.off()

    def off(self):
        self.set_all(0)

    def set_all(self, throttle):
        for m in self.motors:
            m.set_throtle(throttle)


