from libs.i2c_device import I2CDevice
from micropython import const
_VEML6070_ADDR_CMD =const(0x70>>1)
_VEML6070_ADDR_LOW =const(0x71>>1)
_VEML6070_ADDR_HIGH=const(0x73>>1)
_VEML6070_INTEGRATION_TIME={"VEML6070_HALF_T":[0x00,0],"VEML6070_1_T":[0x01,1],"VEML6070_2_T":[0x02,2],"VEML6070_4_T":[0x03,4]}
_VEML6070_RISK_LEVEL={"LOW":[0,560],"MODERATE":[561,1120],"HIGH":[1121,1494],"VERY HIGH":[1495,2054],"EXTREME":[2055,9999]}
class VEML6070:
 def __init__(self,i2c,_veml6070_it="VEML6070_1_T",ack=False):
  if _veml6070_it not in _VEML6070_INTEGRATION_TIME:
   raise ValueError('Integration Time invalid. Valid values are: ',_VEML6070_INTEGRATION_TIME.keys())
  if ack not in(True,False):
   raise ValueError("ACK must be 'True' or 'False'.")
  self._ack=int(ack)
  self._ack_thd=0x00
  self._it=_veml6070_it
  self.i2c_cmd=I2CDevice(i2c,_VEML6070_ADDR_CMD)
  self.i2c_low=I2CDevice(i2c,_VEML6070_ADDR_LOW)
  self.i2c_high=I2CDevice(i2c,_VEML6070_ADDR_HIGH)
  self.buf=bytearray(1)
  self.buf[0]=self._ack<<5|_VEML6070_INTEGRATION_TIME[self._it][0]<<2|0x02
  with self.i2c_cmd as i2c_cmd:
   i2c_cmd.write(self.buf)
 @property
 def read(self):
  read_buf=bytearray(2)
  with self.i2c_low as i2c_low:
   i2c_low.readinto(read_buf,end=1)
  with self.i2c_high as i2c_high:
   i2c_high.readinto(read_buf,start=1)
  uvi=read_buf[1]<<8|read_buf[0]
  return uvi
 def set_ack(self,new_ack=False):
  if new_ack not in(True,False):
   raise ValueError("ACK must be 'True' or 'False'.")
  self._ack=int(new_ack)
  self.buf[0]=(self._ack<<5|self._ack_thd<<4|_VEML6070_INTEGRATION_TIME[self._it][0]<<2|0x02)
  with self.i2c_cmd as i2c_cmd:
   i2c_cmd.write(self.buf)
 def set_ack_threshold(self,new_ack_thd=0):
  if new_ack_thd not in(0,1):
   raise ValueError("ACK Threshold must be '0' or '1'.")
  self._ack_thd=int(new_ack_thd)
  self.buf[0]=(self._ack<<5|self._ack_thd<<4|_VEML6070_INTEGRATION_TIME[self._it][0]<<2|0x02)
  with self.i2c_cmd as i2c_cmd:
   i2c_cmd.write(self.buf)
 def set_integration_time(self,new_it):
  if new_it not in _VEML6070_INTEGRATION_TIME:
   raise ValueError("Integration Time invalid. Valid values are: ",_VEML6070_INTEGRATION_TIME.keys())
  self._it=new_it
  self.buf[0]=(self._ack<<5|self._ack_thd<<4|_VEML6070_INTEGRATION_TIME[new_it][0]<<2|0x02)
  with self.i2c_cmd as i2c_cmd:
   i2c_cmd.write(self.buf)
 def sleep(self):
  self.buf[0]=0x03
  with self.i2c_cmd as i2c_cmd:
   i2c_cmd.write(self.buf)
 def wake(self):
  self.buf[0]=(self._ack<<5|self._ack_thd<<4|_VEML6070_INTEGRATION_TIME[self._it][0]<<2|0x02)
  with self.i2c_cmd as i2c_cmd:
   i2c_cmd.write(self.buf)
 def get_index(self,_raw):
  div=_VEML6070_INTEGRATION_TIME[self._it][1]
  if div==0:
   raise ValueError("[veml6070].get_index only available for Integration Times 1, 2, & 4.","Use [veml6070].set_integration_time(new_it) to change the Integration Time.")
  raw_adj=int(_raw/div)
  for levels in _VEML6070_RISK_LEVEL:
   tmp_range=range(_VEML6070_RISK_LEVEL[levels][0],_VEML6070_RISK_LEVEL[levels][1])
   if raw_adj in tmp_range:
    risk=levels
    break
  return risk
