import ucollections
import utime

class _BaseRTC:
    _SWAP_DAY_WEEKDAY = False
    
    # Weekday 0 is Monday
    DateTimeTuple = ucollections.namedtuple("DateTimeTuple", ["year", "month",
        "day", "weekday", "hour", "minute", "second", "millisecond"])
    
    def __init__(self, i2c, address=0x68):
        self.i2c = i2c
        self.address = address

    def _register(self, register, buffer=None):
        if buffer is None:
            return self.i2c.readfrom_mem(self.address, register, 1)[0]
        self.i2c.writeto_mem(self.address, register, buffer)

    def _flag(self, register, mask, value=None):
        data = self._register(register)
        if value is None:
            return bool(data & mask)
        if value:
            data |= mask
        else:
            data &= ~mask
        self._register(register, bytearray((data,)))
    
    def _bcd2bin(self, value):
        return (value or 0) - 6 * ((value or 0) >> 4)

    def _bin2bcd(self, value):
        return (value or 0) + 6 * ((value or 0) // 10)

    def datetime(self, datetime=None):
        if datetime is None:
            buffer = self.i2c.readfrom_mem(self.address, self._DATETIME_REGISTER, 7)
            if self._SWAP_DAY_WEEKDAY:
                day = buffer[3]
                weekday = buffer[4]
            else:
                day = buffer[4]
                weekday = buffer[3]
            return self.datetime_tuple(
                year = self._bcd2bin(buffer[6]) + 2000,
                month = self._bcd2bin(buffer[5]),
                day = self._bcd2bin(day),
                weekday = self._bcd2bin(weekday),
                hour = self._bcd2bin(buffer[2]),
                minute = self._bcd2bin(buffer[1]),
                second = self._bcd2bin(buffer[0]),)
        datetime = self.datetime_tuple(*datetime)
        buffer = bytearray(7)
        buffer[0] = self._bin2bcd(datetime.second)
        buffer[1] = self._bin2bcd(datetime.minute)
        buffer[2] = self._bin2bcd(datetime.hour)
        if self._SWAP_DAY_WEEKDAY:
            buffer[4] = self._bin2bcd(datetime.weekday)
            buffer[3] = self._bin2bcd(datetime.day)
        else:
            buffer[3] = self._bin2bcd(datetime.weekday)
            buffer[4] = self._bin2bcd(datetime.day)
        buffer[5] = self._bin2bcd(datetime.month)
        buffer[6] = self._bin2bcd(datetime.year - 2000)
        self._register(self._DATETIME_REGISTER, buffer)
    
    def datetime_tuple(self, year=None, month=None, day=None, weekday=None, hour=None, minute=None,
                       second=None, millisecond=None):
        return self.DateTimeTuple(year, month, day, weekday, hour, minute, second, millisecond)
    
    def tuple2seconds(self, datetime):
        return utime.mktime((datetime.year, datetime.month, datetime.day,
            datetime.hour, datetime.minute, datetime.second, datetime.weekday, 0))

    def seconds2tuple(self, seconds):
        (year, month, day, hour, minute, second, weekday, _yday) = utime.localtime(seconds)
        return self.DateTimeTuple(year, month, day, weekday, hour, minute, second, 0)

class PCF8523(_BaseRTC):
    _CONTROL1_REGISTER = 0x00
    _CONTROL2_REGISTER = 0x01
    _CONTROL3_REGISTER = 0x02
    _DATETIME_REGISTER = 0x03
    _ALARM_REGISTER = 0x0a
    _SQUARE_WAVE_REGISTER = 0x0f
    _SWAP_DAY_WEEKDAY = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init()

    def init(self):
        # Enable battery switchover and low-battery detection.
        self._flag(self._CONTROL3_REGISTER, 0b11100000, False)

    def reset(self):
        self._flag(self._CONTROL1_REGISTER, 0x58, True)
        self.init()

    def lost_power(self, value=None):
        return self._flag(self._CONTROL3_REGISTER, 0b00010000, value)

    def stop(self, value=None):
        return self._flag(self._CONTROL1_REGISTER, 0b00010000, value)

    def battery_low(self):
        return self._flag(self._CONTROL3_REGISTER, 0b00000100)

    def alarm(self, value=None):
        return self._flag(self._CONTROL2_REGISTER, 0b00001000, value)

    def datetime(self, datetime=None):
        if datetime is not None:
            self.lost_power(False) # clear the battery switchover flag
        return super().datetime(datetime)

    def alarm_time(self, datetime=None):
        if datetime is None:
            buffer = self.i2c.readfrom_mem(self.address,
                                           self._ALARM_REGISTER, 4)
            return self.datetime_tuple(
                weekday = self._bcd2bin(buffer[3] &
                                 0x7f) if not buffer[3] & 0x80 else None,
                day = self._bcd2bin(buffer[2] &
                             0x7f) if not buffer[2] & 0x80 else None,
                hour = self._bcd2bin(buffer[1] &
                              0x7f) if not buffer[1] & 0x80 else None,
                minute = self._bcd2bin(buffer[0] &
                                0x7f) if not buffer[0] & 0x80 else None,
            )
        datetime = self.datetime_tuple(*datetime)
        buffer = bytearray(4)
        buffer[0] = (self._bin2bcd(datetime.minute)
                     if datetime.minute is not None else 0x80)
        buffer[1] = (self._bin2bcd(datetime.hour)
                     if datetime.hour is not None else 0x80)
        buffer[2] = (self._bin2bcd(datetime.day)
                     if datetime.day is not None else 0x80)
        buffer[3] = (self._bin2bcd(datetime.weekday) | 0b01000000
                     if datetime.weekday is not None else 0x80)
        self._register(self._ALARM_REGISTER, buffer)
