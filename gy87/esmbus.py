import smbus

class ESMBus:
    def __init__(self, address, bus = smbus.SMBus(1)):
        self.address = address
        self.bus = bus

    def reverseByteOrder(self, data):
        # Reverses the byte order of an int (16-bit) or long (32-bit) value
        # Courtesy Vishal Sapre
        dstr = hex(data)[2:].replace('L','')
        byteCount = len(dstr[::2])
        val = 0
        for i, n in enumerate(range(byteCount)):
            d = data & 0xFF
            val |= (d << (8 * (byteCount - i - 1)))
            data >>= 8
        return val

    def readBit(self, reg, bitNum):
        b = self.readU8(reg)
        data = b & (1 << bitNum)
        return data

    def writeBit(self, reg, bitNum, data):
        b = self.readU8(reg)
        if data != 0:
            b = (b | (1 << bitNum))
        else:
            b = (b & ~(1 << bitNum))

        return self.write8(reg, b)

    def readBits(self, reg, bitStart, length):
        # 01101001 read byte
        # 76543210 bit numbers
        #    xxx   args: bitStart=4, length=3
        #    010   masked
        #   -> 010 shifted

        b = self.readU8(reg)
        mask = ((1 << length) - 1) << (bitStart - length + 1)
        b &= mask
        b >>= (bitStart - length + 1)

        return b

    def writeBits(self, reg, bitStart, length, data):
        #      010 value to write
        # 76543210 bit numbers
        #    xxx   args: bitStart=4, length=3
        # 00011100 mask byte
        # 10101111 original value (sample)
        # 10100011 original & ~mask
        # 10101011 masked | value

        b = self.readU8(reg)
        mask = ((1 << length) - 1) << (bitStart - length + 1)
        data <<= (bitStart - length + 1)
        data &= mask
        b &= ~(mask)
        b |= data

        return self.write8(reg, b)

    def readBytes(self, reg, length):
        output = []

        i = 0
        while i < length:
            output.append(self.readU8(reg))
            i += 1

        return output

    def readBytesListU(self, reg, length):
        output = []

        i = 0
        while i < length:
            output.append(self.readU8(reg + i))
            i += 1

        return output

    def readBytesListS(self, reg, length):
        output = []

        i = 0
        while i < length:
            output.append(self.readS8(reg + i))
            i += 1

        return output

    def writeList(self, reg, list):
        # Writes an array of bytes using I2C format"
        try:
            self.bus.write_i2c_block_data(self.address, reg, list)
        except (IOError):
            print ("Error accessing 0x%02X: Check your I2C address" % self.address)
        return -1

    def write8(self, reg, value):
        # Writes an 8-bit value to the specified register/address
        try:
            self.bus.write_byte_data(self.address, reg, value)
        except (IOError):
            print ("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readU8(self, reg):
        # Read an unsigned byte from the I2C device
        try:
            result = self.bus.read_byte_data(self.address, reg)
            return result
        except (IOError):
            print ("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readS8(self, reg):
        # Reads a signed byte from the I2C device
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if result > 127:
                return result - 256
            else:
                return result
        except (IOError):
            print ("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readU16(self, reg, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self.bus.read_word_data(self.address, reg) & 0xFFFF
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, reg, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self.readU16(reg, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def readU16LE(self, reg):
        """Read an unsigned 16-bit value from the specified register, in little
        endian byte order."""
        return self.readU16(reg, little_endian=True)

    def readU16BE(self, reg):
        """Read an unsigned 16-bist value from the specified register, in big
        endian byte order."""
        return self.readU16(reg, little_endian=False)

    def readS16LE(self, reg):
        """Read a signed 16-bit value from the specified register, in little
        endian byte order."""
        return self.readS16(reg, little_endian=True)

    def readS16BE(self, reg):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self.readS16(reg, little_endian=False)