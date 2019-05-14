import time
import math
from machine import Pin
from micropython import const
from libs.i2c_device import I2CDevice 
import struct
DEVICE_ID=const(0x33)
I2C_ADDRESS=const(0x18)
REG_OUTADC1_L =const(0x08)
REG_WHOAMI =const(0x0F)
REG_TEMPCFG =const(0x1F)
REG_CTRL1 =const(0x20)
REG_CTRL3 =const(0x22)
REG_CTRL4 =const(0x23)
REG_CTRL5 =const(0x24)
REG_OUT_X_L =const(0x28)
REG_INT1SRC =const(0x31)
REG_CLICKCFG =const(0x38)
REG_CLICKSRC =const(0x39)
REG_CLICKTHS =const(0x3A)
REG_TIMELIMIT =const(0x3B)
REG_TIMELATENCY=const(0x3C)
REG_TIMEWINDOW =const(0x3D)
RANGE_16_G =const(0b11) 
RANGE_8_G =const(0b10) 
RANGE_4_G =const(0b01) 
RANGE_2_G =const(0b00) 
DATARATE_1344_HZ =const(0b1001) 
DATARATE_400_HZ =const(0b0111) 
DATARATE_200_HZ =const(0b0110) 
DATARATE_100_HZ =const(0b0101) 
DATARATE_50_HZ =const(0b0100) 
DATARATE_25_HZ =const(0b0011) 
DATARATE_10_HZ =const(0b0010) 
DATARATE_1_HZ =const(0b0001) 
DATARATE_POWERDOWN =const(0)
DATARATE_LOWPOWER_1K6HZ =const(0b1000)
DATARATE_LOWPOWER_5KHZ =const(0b1001)
STANDARD_GRAVITY=9.806
class LIS3DH:
 def __init__(self,intPin):
  device_id=self._read_register_byte(REG_WHOAMI)
  if device_id!=DEVICE_ID:
   raise RuntimeError("Failed to find LIS3DH!")
  self._write_register_byte(REG_CTRL5,0x80)
  time.sleep(0.01) 
  self._write_register_byte(REG_CTRL1,0x07)
  self.data_rate=DATARATE_400_HZ
  self._write_register_byte(REG_CTRL4,0x88)
  self._write_register_byte(REG_TEMPCFG,0x80)
  self._write_register_byte(REG_CTRL5,0x08)
  if intPin:
   self._intPin=Pin(intPin,Pin.IN,Pin.PULL_UP)
 @property
 def data_rate(self):
  ctl1=self._read_register_byte(REG_CTRL1)
  return(ctl1>>4)&0x0F
 @data_rate.setter
 def data_rate(self,rate):
  ctl1=self._read_register_byte(REG_CTRL1)
  ctl1&=~(0xF0)
  ctl1|=rate<<4
  self._write_register_byte(REG_CTRL1,ctl1)
 @property
 def range(self):
  ctl4=self._read_register_byte(REG_CTRL4)
  return(ctl4>>4)&0x03
 @range.setter
 def range(self,range_value):
  ctl4=self._read_register_byte(REG_CTRL4)
  ctl4&=~0x30
  ctl4|=range_value<<4
  self._write_register_byte(REG_CTRL4,ctl4)
 def get_acceleration(self,as_mps2=True):
  g=STANDARD_GRAVITY if as_mps2 else 1.0 
  divider=1
  accel_range=self.range
  if accel_range==RANGE_16_G:
   divider=1365
  elif accel_range==RANGE_8_G:
   divider=4096
  elif accel_range==RANGE_4_G:
   divider=8190
  elif accel_range==RANGE_2_G:
   divider=16380
  x,y,z=struct.unpack('<hhh',self._read_register(REG_OUT_X_L|0x80,6))
  x=(x/divider)*g
  y=(y/divider)*g
  z=(z/divider)*g
  return x,y,z
 def shake(self,shake_threshold=30,avg_count=10,total_delay=0.1):
  shake_accel=(0,0,0)
  for _ in range(avg_count):
   shake_accel=tuple(map(sum,zip(shake_accel,self.get_acceleration())))
   time.sleep(total_delay/avg_count)
  avg=tuple(value/avg_count for value in shake_accel)
  total_accel=math.sqrt(sum(map(lambda x:x*x,avg)))
  return total_accel>shake_threshold
 def read_adc_raw(self,adc):
  if adc<1 or adc>3:
   raise ValueError('ADC must be a value 1 to 3!')
  return struct.unpack('<h',self._read_register((REG_OUTADC1_L+((adc-1)*2))|0x80,2))[0]
 def read_adc_mV(self,adc):
  raw=self.read_adc_raw(adc)
  return 1800+(raw+32512)*(-900/65024)
 @property
 def tapped(self):
  if self._intPin and not self._intPin.value():
   return False
  raw=self._read_register_byte(REG_CLICKSRC)
  return raw&0x40>0
 def set_tap(self,tap,threshold,*,time_limit=10,time_latency=20,time_window=255,click_cfg=None):
  if(tap<0 or tap>2)and click_cfg is None:
   raise ValueError('Tap must be 0 (disabled), 1 (single tap), or 2 (double tap)!')
  if threshold>127 or threshold<0:
   raise ValueError('Threshold out of range (0-127)')
  ctrl3=self._read_register_byte(REG_CTRL3)
  if tap==0 and click_cfg is None:
   self._write_register_byte(REG_CTRL3,ctrl3&~(0x80)) 
   self._write_register_byte(REG_CLICKCFG,0)
   return
  else:
   self._write_register_byte(REG_CTRL3,ctrl3|0x80) 
  if click_cfg is None:
   if tap==1:
    click_cfg=0x15 
   if tap==2:
    click_cfg=0x2A 
  self._write_register_byte(REG_CLICKCFG,click_cfg)
  self._write_register_byte(REG_CLICKTHS,0x80|threshold)
  self._write_register_byte(REG_TIMELIMIT,time_limit)
  self._write_register_byte(REG_TIMELATENCY,time_latency)
  self._write_register_byte(REG_TIMEWINDOW,time_window)
 def _read_register_byte(self,register):
  return self._read_register(register,1)[0]
 def _read_register(self,register,length):
  raise NotImplementedError
 def _write_register_byte(self,register,value):
  raise NotImplementedError
class LIS3DH_I2C(LIS3DH):
 def __init__(self,i2c,*,address=I2C_ADDRESS,intPin=None):
  self._i2c=I2CDevice(i2c,address)
  self._buffer=bytearray(6)
  super().__init__(intPin)
 def _read_register(self,register,length):
  self._buffer[0]=register&0xFF
  with self._i2c as i2c:
   i2c.write(self._buffer,start=0,end=1)
   i2c.readinto(self._buffer,start=0,end=length)
   return self._buffer
 def _write_register_byte(self,register,value):
  self._buffer[0]=register&0xFF
  self._buffer[1]=value&0xFF
  with self._i2c as i2c:
   i2c.write(self._buffer,start=0,end=2)
