from bmp180 import BMP180
from hmc5883l import HMC5883L
from mpu6050 import MPU6050
G = 9.81
R = 8.314
LAPSE_RATE = 0.007 # Positive ! (rate of change of temperature per 1 meter)

class Gy87:
    """This class wraps 3 sensors that are available in Gy87:
        Pressure and Temperature sensor - bmp180
        Accelerometer and Gyro - mpu6050
        Compass 3d - Not supported yet
       You this class analyses data from sensors and presents the result in the simplest form:
       For example get_height method gives you the estimated height based on bmp180 measurements
    """
    NAME = 'Gy87'

    def __init__(self):
        self.bmp = BMP180()
        self.hmc = HMC5883L()
        self.mpu = MPU6050()
        #Get ground pressure and temperature
        self.pressure0 = self.get_pressure(3)
        self.temperature0 = self.get_temperature(3)

    def get_temperature(self, n=1):
        """returns temperature in celsius"""
        self.temperature = self.average(self.bmp.read_temperature, n)
        return self.temperature

    def get_pressure(self, n=1):
        """returns pressure in pascals"""
        self.pressure = self.average(self.bmp.read_pressure, n)
        return self.pressure

    def get_heading(self, n=1):
        """gets heading direction from compass x, y, z"""
        self.heading = self.average(self.hmc.getHeading(), n)
        return self.heading

    # Sensor independent methods
    def average(self, meth, n=3):
        """returns average of n measurements"""
        return sum(meth() for e in xrange(n))/float(n)

    def get_height(self):
        """ Not very accurate.., returns height above ground in meters"""
        p = self.get_pressure(2)
        return (self.temperature0+273)/LAPSE_RATE*(1-(p/self.pressure0)**(R*LAPSE_RATE/G/0.02896))

    def test(self):
        print 20*'-'
        print 'Started test testing %s sensor...' % self.NAME
        print
        print 'Pressure and Temperature sensor:'
        try:
            r = self.get_pressure(), self.get_temperature()
            print 'OK  %s'%str(r)
        except:
            print 'FAILED'
        print
        print 'Accelerometer and Gyro:'
        try:
            r = self.get_acc(), self.get_angacc()
            print 'OK  %s'%str(r)
        except:
            print 'FAILED'
        print
        print 'Compass:'
        try:
            r = self.get_heading()
            print 'OK  %s'%str(r)
        except:
            print 'FAILED'

