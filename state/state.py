from ultrasonic import Ultrasonic, measure_loop
from gy87.bmp180 import BMP180
import time
import threading
from math import *

b = BMP180()
t = 0
for n in xrange(100):
    t += b.read_pressure()
    time.sleep(0.01)
P0 = t / 100.0
T0 = b.read_temperature()
G = 9.81
R = 8.314
LAPSE_RATE = 0.007  # Positive ! (rate of change of temperature per 1 meter)


class Barometer:
    def __init__(self):
        self.__t = threading.Thread(target=self._updater)
        self.__t.daemon = True
        self.__t.start()

    def _updater(self):
        while 1:
            p = b.read_pressure()
            self.last_pressure = (T0 + 273.0) / LAPSE_RATE * (1 - (p / P0) ** (R * LAPSE_RATE / G / 0.02896))

    def get_altitude(self):
        return self.last_pressure


ultra = Ultrasonic(measure_loop)
ultra.measure()

bar = 0#Barometer()
import time
import random
import numpy as np
# import altitude
from math import *

KH = 100
KV = 50

HOST = "localhost"
PORT = 4223
UID = '6qYGR7'  # Change to your UID
GIMU = 9.80605
from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_imu import BrickIMU

ipcon = IPConnection()
imu = BrickIMU(UID, ipcon)
ipcon.connect(HOST, PORT)


def calc_acc():
    x, y, z = imu.get_acceleration()
    return (x * x + y * y + z * z) ** 0.5


ss = [calc_acc() for e in xrange(100)]

print np.array(ss).std() / 1000 * 9.81

GF = sum(ss) / 100.0 / 1000.0


def v_av(v1, v2, k):
    return (v1 + k * v2) / (k + 1.0)


class State:
    Ve = 0
    He = 0
    on_updated_state = None
    yaw = pitch = roll = 0  # Positive Pitch = Right. Negative Roll = Forward, Positive Yaw= Left

    def __init__(self, imu=imu, T=0.02):
        # Update period
        self.T = T

        # IMU
        imu.leds_off()
        imu.orientation_calculation_off()
        imu.disable_status_led()
        self.imu = imu

    def run(self):
        n = 0
        self.next_run = time.time() + self.T
        while True:
            n += 1
            wait = self.next_run - time.time()
            if wait > 0:
                time.sleep(wait)
                self.next_run += self.T
            else:
                print 'LATE!!!'
                # allow recovery...
                self.next_run = time.time() + self.T
            self.update()
            # print self.He, self.Ve

    # Update measurements and compute new altitude every 6ms.
    def update(self):
        self.q = self.imu.get_quaternion()
        x, y, z, w = self.q
        self.yaw = -atan2(2 * x * y + 2 * w * z, w * w + x * x - y * y - z * z) / 3.14 * 180.0
        self.pitch = -asin(2 * w * y - 2 * x * z) / 3.14 * 180.0
        self.roll = -atan2(2 * y * z + 2 * w * x, -w * w + x * x + y * y - z * z) / 3.14 * 180.0
        xa,ya,za = self.imu.get_angular_velocity()
        self.xa = xa/14.375
        self.ya = ya/14.375
        self.za = za/14.375

        self.acc = self.imu.get_acceleration()

        self.net_acc = self.compute_compensated_acc(self.q, self.acc)
        self.net_earth_acc = self.compute_dynamic_acceleration_vector(self.q, self.net_acc)
        self.update_vertical_estimates()
        if self.on_updated_state:
            self.on_updated_state(self)

    # Remove gravity from accelerometer measurements
    def compute_compensated_acc(self, q, a):
        g = (2 * (q.x * q.z - q.w * q.y),
             2 * (q.w * q.x + q.y * q.z),
             q.w * q.w - q.x * q.x - q.y * q.y + q.z * q.z)

        return ((a[0] / 1000.0 - GF * g[0]) * GIMU,
                (a[1] / 1000.0 - GF * g[1]) * GIMU,
                (a[2] / 1000.0 - GF * g[2]) * GIMU,
                0.0)

    # Rotate dynamic acceleration vector from sensor frame to earth frame
    def compute_dynamic_acceleration_vector(self, q, compensated_acc_q):
        def q_conj(q):
            return -q[0], -q[1], -q[2], q[3]

        def q_mult(q1, q2):
            x1, y1, z1, w1 = q1
            x2, y2, z2, w2 = q2
            w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
            x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
            y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
            z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2

            return x, y, z, w

        tmp = q_mult(q, compensated_acc_q)
        return q_mult(tmp, q_conj(q))

    def get_barometric_altitude(self):
        # MUST RETURN INSTANTLY!!!
        # return np.random.normal(0,0.20)
        #return bar.get_altitude()
        return 0

    def get_ultrasonic_altitude(self):
        # MUST RETURN INSTANTLY!!!
        u = ultra.get_height()
        # ultra.height = None
        return u

    def update_vertical_estimates(self):  # piotr's filter: easy to understand and good!
        H1 = self.get_barometric_altitude()  # Huge std of 20cm
        HT = self.get_ultrasonic_altitude()
        # print H1
        H2 = self.He + self.Ve * self.T + self.T ** 2 * self.net_earth_acc[2] / 2.0  # this std is quite small 5cm
        if HT is None:
            #print 'Using pressure...'
            He2 = v_av(H1, H2, KH)  # estimate height using above 2 values...
        else:  # use much more accurate ultrasonic measurement!
            He2 = v_av(H2, HT, 3)
        V1 = (He2 - self.He) / self.T  # this val has 10cm/t srd
        V2 = self.Ve + self.T * self.net_earth_acc[2]  # Again this one has small std of 10cm/s
        self.He, self.Ve = He2, v_av(V1, V2, KV)




if __name__=='__main__':
    s = State()
    s.run()