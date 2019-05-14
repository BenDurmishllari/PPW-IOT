import math
from machine import Pin
class DotStar:
 def __init__(self,spi,cpin=None,dpin=None,*,n,brightness=1.0,auto_write=True):
  self._spi=spi
  if not self._spi: 
   self.cpin=cpin
   self.dpin=dpin
   if not self.cpin or not self.dpin: 
    raise ValueError("Must supply both clock and data pins if not using SPI!")
   self.cpin.init(mode=Pin.OUT)
   self.dpin.init(mode=Pin.OUT)
   self.cpin.value(False)
  self._n=n
  self.start_header_size=4
  self.end_header_size=n//16
  if n%16!=0:
   self.end_header_size+=1
  self._buf=bytearray(n*4+self.start_header_size+self.end_header_size)
  self.end_header_index=len(self._buf)-self.end_header_size
  for i in range(self.start_header_size):
   self._buf[i]=0x00
  for i in range(self.start_header_size,self.end_header_index,4):
   self._buf[i]=0xff
  for i in range(self.end_header_index,len(self._buf)):
   self._buf[i]=0xff
  self._brightness=1.0
  self.brightness=brightness
  self.auto_write=auto_write
 def deinit(self):
  self.auto_write=False
  for i in range(self.start_header_size,self.end_header_index):
   if i%4!=0:
    self._buf[i]=0
  self.show()
  if self._spi:
   self._spi.deinit()
 def __enter__(self):
  return self
 def __exit__(self,exception_type,exception_value,traceback):
  self.deinit()
 def __repr__(self):
  return "["+", ".join([str(x)for x in self])+"]"
 def _set_item(self,index,value):
  offset=index*4+self.start_header_size
  r=0
  g=0
  b=0
  if isinstance(value,int):
   r=value>>16
   g=(value>>8)&0xff
   b=value&0xff
  else:
   r,g,b=value
  self._buf[offset]=0xff 
  self._buf[offset+1]=b
  self._buf[offset+2]=g
  self._buf[offset+3]=r
 def __setitem__(self,index,val):
  if isinstance(index,slice):
   start,stop,step=index.indices(len(self))
   length=stop-start
   if step!=0:
    length=math.ceil(length/step)
   if len(val)!=length:
    raise ValueError("Slice and input sequence size do not match.")
   for val_i,in_i in enumerate(range(start,stop,step)):
    self._set_item(in_i,val[val_i])
  else:
   self._set_item(index,val)
  if self.auto_write:
   self.show()
 def __getitem__(self,index):
  if isinstance(index,slice):
   out=[]
   for in_i in range(*index.indices(len(self._buf)//4)):
    out.append(tuple(self._buf[in_i*4+(3-i)+self.start_header_size]for i in range(3)))
   return out
  if index<0:
   index+=len(self)
  if index>=self._n or index<0:
   raise IndexError
  offset=index*4
  return tuple(self._buf[offset+(3-i)+self.start_header_size]for i in range(3))
 def __len__(self):
  return self._n
 @property
 def brightness(self):
  return self._brightness
 @brightness.setter
 def brightness(self,brightness):
  self._brightness=min(max(brightness,0.0),1.0)
 def fill(self,color):
  auto_write=self.auto_write
  self.auto_write=False
  for i,_ in enumerate(self):
   self[i]=color
  if auto_write:
   self.show()
  self.auto_write=auto_write
 def _ds_writebytes(self,buf):
  for b in buf:
   for _ in range(8):
    self.cpin.value(True)
    self.dpin.value(b&0x80)
    self.cpin.value(False)
    b=b<<1
 def show(self):
  buf=self._buf
  if self.brightness<1.0:
   buf=bytearray(self._buf)
   for i in range(self.start_header_size):
    buf[i]=0x00
   for i in range(self.start_header_size,self.end_header_index):
    buf[i]=self._buf[i]if i%4==0 else int(self._buf[i]*self._brightness)
   for i in range(self.end_header_index,len(buf)):
    buf[i]=0xff
  if self._spi:
   self._spi.write(buf)
  else:
   self._ds_writebytes(buf)
   self.cpin.value(False)
