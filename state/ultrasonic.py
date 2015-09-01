import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BCM)
TRIG = 17
ECHO = 18
TIMEOUT = 0.035 # up to 6 meters
MEASUREMENT_INTERVAL = 0.2 # up to 5 measurements per second.

class Ultrasonic:
    def __init__(self, on_done=None):
        self.last_measurement_time = 0
        self.GPIO = GPIO
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        GPIO.output(TRIG, False)
        self.height = None
        self.on_done = on_done
        self._RUNNING = False

    def get_height(self):
        return self.height

    def measure(self):
        """Starts measurement process and returns None. When done calls on_done function with (self, height) and updates height attribute.
           Height is in meters.
        """
        if self._RUNNING:
            return
        self._RUNNING = True
        self._t = threading.Thread(target=self._measure)
        self._t.deamon = True
        self._t.start()

    def _measure(self):
        distance = self._get_distance()
        self._RUNNING = False
        if self.on_done:
            self.on_done(self, distance)
        self.height = distance


    def _get_distance(self):
        wait = self.last_measurement_time + MEASUREMENT_INTERVAL - time.time()
        if  wait>0:
            time.sleep(wait)
        self.last_measurement_time = time.time()
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        pulse_start = time.time()
        fail = pulse_start + TIMEOUT
        while GPIO.input(ECHO) == 0:
            if pulse_start > fail:
                return
        pulse_end = time.time()
        fail = pulse_end + TIMEOUT
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if pulse_end > fail:
                return
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return distance / 100.0

    def __del__(self):
        self.GPIO.cleanup()

def measure_loop(ultra, height):
    ultra.measure()

if __name__=='__main__':
    def on_finish(ultra, height):
        print height
        ultra.measure()

    u = Ultrasonic(on_finish)
    u.measure()
    time.sleep(100)



