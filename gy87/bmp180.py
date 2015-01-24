# This module allows you to read data from BMP180 pressure sensor with your raspberry pi. Should work with BMP too.

import time
import esmbus


# BMP default address.
BMP_I2CADDR           = 0x77

# Operating Modes
BMP_ULTRALOWPOWER     = 0
BMP_STANDARD          = 1
BMP_HIGHRES           = 2
BMP_ULTRAHIGHRES      = 3

# BMP Registers
BMP_CAL_AC1           = 0xAA  # R   Calibration data (16 bits)
BMP_CAL_AC2           = 0xAC  # R   Calibration data (16 bits)
BMP_CAL_AC3           = 0xAE  # R   Calibration data (16 bits)
BMP_CAL_AC4           = 0xB0  # R   Calibration data (16 bits)
BMP_CAL_AC5           = 0xB2  # R   Calibration data (16 bits)
BMP_CAL_AC6           = 0xB4  # R   Calibration data (16 bits)
BMP_CAL_B1            = 0xB6  # R   Calibration data (16 bits)
BMP_CAL_B2            = 0xB8  # R   Calibration data (16 bits)
BMP_CAL_MB            = 0xBA  # R   Calibration data (16 bits)
BMP_CAL_MC            = 0xBC  # R   Calibration data (16 bits)
BMP_CAL_MD            = 0xBE  # R   Calibration data (16 bits)
BMP_CONTROL           = 0xF4
BMP_TEMPDATA          = 0xF6
BMP_PRESSUREDATA      = 0xF6

# Commands
BMP_READTEMPCMD       = 0x2E
BMP_READPRESSURECMD   = 0x34

class BMP180:
    # Datasheet calibration
    cal_AC1 = 408
    cal_AC2 = -72
    cal_AC3 = -14383
    cal_AC4 = 32741
    cal_AC5 = 32757
    cal_AC6 = 23153
    cal_B1 = 6190
    cal_B2 = 4
    cal_MB = -32767
    cal_MC = -8711
    cal_MD = 2868
    
    def __init__(self, address=BMP_I2CADDR, mode=BMP_STANDARD, calibrate=True):
        assert mode in range(4)
        self.mode = mode
        bus = esmbus.ESMBus(address)
        self.bus = bus
        if calibrate:
            self._calibrate()

    def _calibrate(self):
        self.cal_AC1 = self.bus.readS16BE(BMP_CAL_AC1)   # INT16
        self.cal_AC2 = self.bus.readS16BE(BMP_CAL_AC2)   # INT16
        self.cal_AC3 = self.bus.readS16BE(BMP_CAL_AC3)   # INT16
        self.cal_AC4 = self.bus.readU16BE(BMP_CAL_AC4)   # UINT16
        self.cal_AC5 = self.bus.readU16BE(BMP_CAL_AC5)   # UINT16
        self.cal_AC6 = self.bus.readU16BE(BMP_CAL_AC6)   # UINT16
        self.cal_B1 = self.bus.readS16BE(BMP_CAL_B1)     # INT16
        self.cal_B2 = self.bus.readS16BE(BMP_CAL_B2)     # INT16
        self.cal_MB = self.bus.readS16BE(BMP_CAL_MB)     # INT16
        self.cal_MC = self.bus.readS16BE(BMP_CAL_MC)     # INT16
        self.cal_MD = self.bus.readS16BE(BMP_CAL_MD)     # INT16

    def read_raw_temp(self):
        """Reads the raw (uncompensated) temperature from the sensor."""
        self.bus.write8(BMP_CONTROL, BMP_READTEMPCMD)
        time.sleep(0.005)  # Wait 5ms
        raw = self.bus.readU16BE(BMP_TEMPDATA)
        return raw
    
    def read_raw_pressure(self):
        """Reads the raw (uncompensated) pressure level from the sensor."""
        self.bus.write8(BMP_CONTROL, BMP_READPRESSURECMD + (self.mode << 6))
        if self.mode == BMP_ULTRALOWPOWER:
            time.sleep(0.005)
        elif self.mode == BMP_HIGHRES:
            time.sleep(0.014)
        elif self.mode == BMP_ULTRAHIGHRES:
            time.sleep(0.026)
        else:
            time.sleep(0.008)
        msb = self.bus.readU8(BMP_PRESSUREDATA)
        lsb = self.bus.readU8(BMP_PRESSUREDATA+1)
        xlsb = self.bus.readU8(BMP_PRESSUREDATA+2)
        raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.mode)
        return raw
    
    def read_temperature(self):
        """Gets the compensated temperature in degrees celsius."""
        UT = self.read_raw_temp()
        # Datasheet value for debugging:
        #UT = 27898
        # Calculations below are taken straight from section 3.5 of the datasheet.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) / (X1 + self.cal_MD)
        B5 = X1 + X2
        temp = ((B5 + 8) >> 4) / 10.0
        return temp
    
    def read_pressure(self):
        """Gets the compensated pressure in Pascals."""
        UT = self.read_raw_temp()
        UP = self.read_raw_pressure()
        # Datasheet values for debugging:
        #UT = 27898
        #UP = 23843
        # Calculations below are taken straight from section 3.5 of the datasheet.
        # Calculate true temperature coefficient B5.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) / (X1 + self.cal_MD)
        B5 = X1 + X2
        # Pressure Calculations
        B6 = B5 - 4000
        X1 = (self.cal_B2 * (B6 * B6) >> 12) >> 11
        X2 = (self.cal_AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.cal_AC1 * 4 + X3) << self.mode) + 2) / 4
        X1 = (self.cal_AC3 * B6) >> 13
        X2 = (self.cal_B1 * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.cal_AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> self.mode)
        if B7 < 0x80000000:
            p = (B7 * 2) / B4
        else:
            p = (B7 / B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        return p
    
    def read_altitude(self, sealevel_pa=101325.0):
        """Calculates the altitude in meters."""
        # Calculation taken straight from section 3.6 of the datasheet.
        pressure = float(self.read_pressure())
        altitude = 44330.0 * (1.0 - pow(pressure / sealevel_pa, (1.0/5.255)))
        return altitude
    
    def read_sealevel_pressure(self, altitude_m=0.0):
        """Calculates the pressure at sealevel when given a known altitude in
        meters. Returns a value in Pascals."""
        pressure = float(self.read_pressure())
        p0 = pressure / pow(1.0 - altitude_m/44330.0, 5.255)
        return p0