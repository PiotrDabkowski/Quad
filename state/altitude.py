"""
Here I am to fusing the data from IMU and Barometer to obtain best estimate of altitude.
I am using Kalman filter.

Results from ultrasonic sensor can be added to obtain even better estimate.
"""
import numpy as np

Q = np.matrix([[0.0,0,0],
               [0,0.0,0],
               [0,0,0.0]])

R = np.matrix([[0.1696623310143,0],
               [0,0.00373674055865]])




class AltitudeKalman:
    def __init__(self, T):
        """Results are in the form  h,a,v,
          Measurement must be in h,a format"""
        self.T = T
        self.A = np.matrix([[1,T*T/2.0,T],
                            [0,1,0],
                            [0,T,1]])
        self.AT = self.A.T

        self.C = np.matrix([[1,0,0],
                            [0,1,0]])
        self.CT = self.C.T

        self.Xe = np.matrix([[0],[0],[0]])
        self.Pe = np.matrix([[0,0,0],
                             [0,0,0],
                             [0,0,0]])

    def update(self, measurement):
        """
        Measurement must be in h,a format
        """
        Xp = self.A * self.Xe
        Pp = self.A*self.Pe+self.AT + Q
        K = Pp * self.CT * (self.C*Pp*self.CT + R).I

        self.Xe = Xp + K*(measurement - self.C*Xp)
        self.Pe = Pp - K*self.C*Pp
        return self.Xe


import time

class Altitude2:
     initialised = False

     def compute_altitude(self, compensated_acceleration, altitude):
        self.current_time = time.time()

        # Initialization
        if not self.initialized:
            self.initialized = True
            self.estimated_altitude = altitude
            self.estimated_velocity = 0
            self.altitude_error_i = 0

        # Estimation Error
        self.altitude_error = altitude - self.estimated_altitude
        self.altitude_error_i = self.altitude_error_i + self.altitude_error
        self.altitude_error_i = min(2500.0, max(-2500.0, self.altitude_error_i))

        self.inst_acceleration = compensated_acceleration * 9.80665 + self.altitude_error_i * self.KI
        dt = self.current_time - self.last_time

        # Integrators
        self.delta = self.inst_acceleration * dt + (self.KP1 * dt) * self.altitude_error
        self.estimated_altitude += (self.estimated_velocity/5.0 + self.delta) * (dt / 2) + (self.KP2 * dt) * self.altitude_error
        self.estimated_velocity += self.delta*10.0

        self.last_time = self.current_time

        return self.estimated_altitude








