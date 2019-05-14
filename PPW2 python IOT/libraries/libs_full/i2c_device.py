class I2CDevice:
    """
    Represents a single I2C device and manages operating the bus and the device address

    :param machine.I2C i2c: The I2C bus the device is on
    :param int device_address: The 7 bit device address
    """
    def __init__(self, i2c, device_address):
        self.i2c = i2c
        self.device_address = device_address

    def readinto(self, buf, start=None, end=None, stop=True):
        """
        Read into buf from the device, the number of bytes read will be the length of buf or if
        start and/or end is provided, then the buffer will be sliced as if using buf[start:end]

        :param bytearray buffer: buffer to write into
        :param int start: Index to start writing at
        :param int end: Index to write up to but not include
        :param bool stop: If true, output an I2C stop condition after the buffer is read
        """
        s = 0
        e = len(buf)
        if start:
            s = start
            
        if end:
            e = end
        
        b = bytearray(e - s)
        
        self.i2c.readfrom_into(self.device_address, b, stop)
        
        buf[s:e] = b[:]

        # for i in range(s, e):
            # buf[i] = b[i - s]

    def write(self, buf, start=None, end=None, stop=True):
        """
        Write the bytes from buffer to the device, transmits a stop bit if stop is set, if
        start and/or end is provided, then the buffer will be sliced as if using buf[start:end]

        :param bytearray buffer: buffer containing the bytes to write
        :param int start: Index to start writing from
        :param int end: Index to read up to but not include
        :param bool stop: If true, output an I2C stop condition after the buffer is written
        """
        s = 0
        e = len(buf)
        if start:
            s = start
            
        if end:
            e = end
        
        self.i2c.writeto(self.device_address, buf[s:e], stop)

    def __enter__(self):
        """
        To be ignored
        """
        return self

    def __exit__(self, *exc):
        """
        To be ignored
        """
        return False
