#!/usr/bin/python
import time
import math
import re
import smbus

# ===========================================================================
# Adafruit_I2C Class
# ===========================================================================

class Adafruit_I2C(object):

  @staticmethod
  def getPiRevision():
    "Gets the version number of the Raspberry Pi board"
    # Revision list available at: http://elinux.org/RPi_HardwareHistory#Board_Revision_History
    try:
      with open('/proc/cpuinfo', 'r') as infile:
        for line in infile:
          # Match a line of the form "Revision : 0002" while ignoring extra
          # info in front of the revsion (like 1000 when the Pi was over-volted).
          match = re.match('Revision\s+:\s+.*(\w{4})$', line)
          if match and match.group(1) in ['0000', '0002', '0003']:
            # Return revision 1 if revision ends with 0000, 0002 or 0003.
            return 1
          elif match:
            # Assume revision 2 if revision ends with any other 4 chars.
            return 2
        # Couldn't find the revision, assume revision 0 like older code for compatibility.
        return 0
    except:
      return 0

  @staticmethod
  def getPiI2CBusNumber():
    # Gets the I2C bus number /dev/i2c#
    return 1 if Adafruit_I2C.getPiRevision() > 1 else 0

  def __init__(self, address, busnum=-1, debug=False):
    self.address = address
    # By default, the correct I2C bus is auto-detected using /proc/cpuinfo
    # Alternatively, you can hard-code the bus version below:
    # self.bus = smbus.SMBus(0); # Force I2C0 (early 256MB Pi's)
    # self.bus = smbus.SMBus(1); # Force I2C1 (512MB Pi's)
    self.bus = smbus.SMBus(busnum if busnum >= 0 else Adafruit_I2C.getPiI2CBusNumber())
    self.debug = debug

  def reverseByteOrder(self, data):
    "Reverses the byte order of an int (16-bit) or long (32-bit) value"
    # Courtesy Vishal Sapre
    byteCount = len(hex(data)[2:].replace('L','')[::2])
    val       = 0
    for i in range(byteCount):
      val    = (val << 8) | (data & 0xff)
      data >>= 8
    return val

  def errMsg(self):
    print "Error accessing 0x%02X: Check your I2C address" % self.address
    return -1

  def write8(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    try:
      self.bus.write_byte_data(self.address, reg, value)
      if self.debug:
        print "I2C: Wrote 0x%02X to register 0x%02X" % (value, reg)
    except IOError, err:
      return self.errMsg()

  def write16(self, reg, value):
    "Writes a 16-bit value to the specified register/address pair"
    try:
      self.bus.write_word_data(self.address, reg, value)
      if self.debug:
        print ("I2C: Wrote 0x%02X to register pair 0x%02X,0x%02X" %
         (value, reg, reg+1))
    except IOError, err:
      return self.errMsg()

  def writeRaw8(self, value):
    "Writes an 8-bit value on the bus"
    try:
      self.bus.write_byte(self.address, value)
      if self.debug:
        print "I2C: Wrote 0x%02X" % value
    except IOError, err:
      return self.errMsg()

  def writeList(self, reg, list):
    "Writes an array of bytes using I2C format"
    try:
      if self.debug:
        print "I2C: Writing list to register 0x%02X:" % reg
        print list
      self.bus.write_i2c_block_data(self.address, reg, list)
    except IOError, err:
      return self.errMsg()

  def readList(self, reg, length):
    "Read a list of bytes from the I2C device"
    try:
      results = self.bus.read_i2c_block_data(self.address, reg, length)
      if self.debug:
        print ("I2C: Device 0x%02X returned the following from reg 0x%02X" %
         (self.address, reg))
        print results
      return results
    except IOError, err:
      return self.errMsg()

  def readU8(self, reg):
    "Read an unsigned byte from the I2C device"
    try:
      result = self.bus.read_byte_data(self.address, reg)
      if self.debug:
        print ("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" %
         (self.address, result & 0xFF, reg))
      return result
    except IOError, err:
      return self.errMsg()

  def readS8(self, reg):
    "Reads a signed byte from the I2C device"
    try:
      result = self.bus.read_byte_data(self.address, reg)
      if result > 127: result -= 256
      if self.debug:
        print ("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" %
         (self.address, result & 0xFF, reg))
      return result
    except IOError, err:
      return self.errMsg()

  def readU16(self, reg, little_endian=True):
    "Reads an unsigned 16-bit value from the I2C device"
    try:
      result = self.bus.read_word_data(self.address,reg)
      # Swap bytes if using big endian because read_word_data assumes little 
      # endian on ARM (little endian) systems.
      if not little_endian:
        result = ((result << 8) & 0xFF00) + (result >> 8)
      if (self.debug):
        print "I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, result & 0xFFFF, reg)
      return result
    except IOError, err:
      return self.errMsg()

  def readS16(self, reg, little_endian=True):
    "Reads a signed 16-bit value from the I2C device"
    try:
      result = self.readU16(reg,little_endian)
      if result > 32767: result -= 65536
      return result
    except IOError, err:
      return self.errMsg()

if __name__ == '__main__':
  try:
    bus = Adafruit_I2C(address=0)
    print "Default I2C bus is accessible"
  except:
    print "Error accessing default I2C bus"


# ============================================================================
# Adafruit PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PWM:
    __MODE1 = 0x00
    __MODE2 = 0x01
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALL_LED_ON_L = 0xFA
    __ALL_LED_ON_H = 0xFB
    __ALL_LED_OFF_L = 0xFC
    __ALL_LED_OFF_H = 0xFD

    # Bits
    __RESTART = 0x80
    __SLEEP = 0x10
    __ALLCALL = 0x01
    __INVRT = 0x10
    __OUTDRV = 0x04

    def __init__(self, address=0x40, freq=50):
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.setAllPWM(0, 0)
        self.i2c.write8(self.__MODE2, self.__OUTDRV)
        self.i2c.write8(self.__MODE1, self.__ALLCALL)
        time.sleep(0.005)  # wait for oscillator
        mode1 = self.i2c.readU8(self.__MODE1)
        mode1 = mode1 & ~self.__SLEEP  # wake up (reset sleep)
        self.i2c.write8(self.__MODE1, mode1)
        time.sleep(0.005)  # wait for oscillator
        self.setPWMFreq(freq)

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)
        oldmode = self.i2c.readU8(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.i2c.write8(self.__MODE1, newmode)  # go to sleep
        self.i2c.write8(self.__PRESCALE, int(math.floor(prescale)))
        self.i2c.write8(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.i2c.write8(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.i2c.write8(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.i2c.write8(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.i2c.write8(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.i2c.write8(self.__LED0_OFF_H + 4 * channel, off >> 8)


    def setAllPWM(self, on, off):
        "Sets a all PWM channels"
        self.i2c.write8(self.__ALL_LED_ON_L, on & 0xFF)
        self.i2c.write8(self.__ALL_LED_ON_H, on >> 8)
        self.i2c.write8(self.__ALL_LED_OFF_L, off & 0xFF)
        self.i2c.write8(self.__ALL_LED_OFF_H, off >> 8)  # Initialise the PWM device using the default address

    def set_throttle(self, channel, throttle):
        '''throttle is a float from 0 to 1000. Its specific for my motors:
          PWM frequency 50hz and Pulse form 1000us to 2000us.'''
        self.setPWM(channel, 0, (1000+throttle)*4096/20000)



_driver = PWM()


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
        self.motors = [Motor(e) for e in xrange(4)]
        self._a, self._b, self._c, self._d = self.motors
        self.off()

    def off(self):
        self.set_all(0)

    def set_all(self, throttle):
        for m in self.motors:
            m.set_throttle(throttle)

    def __del__(self):
        for m in self.motors:
           m.set_throttle(0)



m = Motors()
m.off()
time.sleep(3)
m.set_all(200)
time.sleep(0.5)
m.off()
time.sleep(2)
m.set_all(200)
time.sleep(0.5)
m.off()
