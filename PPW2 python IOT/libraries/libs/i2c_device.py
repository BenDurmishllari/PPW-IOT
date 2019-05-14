class I2CDevice:
 def __init__(self,i2c,device_address):
  self.i2c=i2c
  self.device_address=device_address
 def readinto(self,buf,start=None,end=None,stop=True):
  s=0
  e=len(buf)
  if start:
   s=start
  if end:
   e=end
  b=bytearray(e-s)
  self.i2c.readfrom_into(self.device_address,b,stop)
  buf[s:e]=b[:]
 def write(self,buf,start=None,end=None,stop=True):
  s=0
  e=len(buf)
  if start:
   s=start
  if end:
   e=end
  self.i2c.writeto(self.device_address,buf[s:e],stop)
 def __enter__(self):
  return self
 def __exit__(self,*exc):
  return False
