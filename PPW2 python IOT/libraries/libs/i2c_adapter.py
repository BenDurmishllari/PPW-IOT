from machine import I2C
class I2CAdapter(I2C):
 def read_byte_data(self,addr,register):
  return self.readfrom_mem(addr,register,1)[0]
 def read_i2c_block_data(self,addr,register,length):
  return self.readfrom_mem(addr,register,length)
 def write_byte_data(self,addr,register,data):
  return self.writeto_mem(addr,register,bytearray([data]))
 def write_i2c_block_data(self,addr,register,data):
  return self.writeto_mem(addr,register,bytearray([data]))
