from binascii import hexlify
from machine import Pin,I2C,SPI,unique_id
from libs.i2c_adapter import I2CAdapter
from libs.i2c_device import I2CDevice
from libs.ssd1306 import SSD1306_I2C as SSD1306
class ProtoRig:
 DEFAULT_NAME="ProtoRig"
 PIN_4=Pin(4) 
 PIN_5=Pin(5) 
 PIN_12=Pin(12,Pin.OUT) 
 PIN_13=Pin(13) 
 PIN_14=Pin(14) 
 PIN_15=Pin(15) 
 PIN_16=Pin(16) 
 PIN_17=Pin(17) 
 PIN_18=Pin(18) 
 PIN_19=Pin(19) 
 PIN_21=Pin(21) 
 PIN_22=Pin(22) 
 PIN_23=Pin(23) 
 PIN_25=Pin(25) 
 PIN_26=Pin(26) 
 PIN_27=Pin(27) 
 PIN_32=Pin(32) 
 PIN_33=Pin(33) 
 PIN_34=Pin(34,Pin.IN) 
 PIN_36=Pin(36,Pin.IN) 
 PIN_39=Pin(39,Pin.IN) 
 PIN_DAC1=PIN_25 
 PIN_DAC2=PIN_26 
 PIN_A0=PIN_DAC2 
 PIN_A1=PIN_DAC1 
 PIN_A2=PIN_34 
 PIN_A3=PIN_39 
 PIN_A4=PIN_36 
 PIN_A5=PIN_4 
 PIN_A6=PIN_14 
 PIN_A7=PIN_32 
 PIN_A8=PIN_15 
 PIN_A9=PIN_33 
 PIN_A10=PIN_27 
 PIN_A11=PIN_12 
 PIN_A12=PIN_13 
 PIN_SCL=PIN_22 
 PIN_SDA=PIN_23 
 PIN_RX=PIN_16 
 PIN_TX=PIN_17 
 PIN_SCK=PIN_5 
 PIN_MOSI=PIN_18 
 PIN_MISO=PIN_19 
 PIN_VBAT=Pin(35) 
 DEFAULT_I2C_SCL_PIN_NUM=22
 DEFAULT_I2C_SDA_PIN_NUM=23
 DEFAULT_I2C_FREQUENCY=4000000 
 SSPI=-1 
 HSPI=1 
 VSPI=2 
 DEFAULT_SPI_SCK_PIN_NUM=5
 DEFAULT_SPI_MOSI_PIN_NUM=18
 DEFAULT_SPI_MISO_PIN_NUM=19
 DEFAULT_SPI_FREQUENCY=4000000 
 DEFAULT_SPI_POLARITY=0 
 DEFAULT_SPI_PHASE=0
 DEFAULT_SPI_BITS=8
 DEFAULT_SPI_FIRST_BIT=SPI.MSB
 DEFAULT_BUTTON_A_PIN_NUM=15
 DEFAULT_BUTTON_B_PIN_NUM=32
 DEFAULT_BUTTON_C_PIN_NUM=14
 DEFAULT_OLED_WIDTH=128
 DEFAULT_OLED_HEIGHT=32
 def __init__(self,has_oled_board,rig_name=DEFAULT_NAME,i2c_scl_pin_num=DEFAULT_I2C_SCL_PIN_NUM,i2c_sda_pin_num=DEFAULT_I2C_SDA_PIN_NUM,i2c_freq=DEFAULT_I2C_FREQUENCY,btnA_pin_num=DEFAULT_BUTTON_A_PIN_NUM,btnB_pin_num=DEFAULT_BUTTON_B_PIN_NUM,btnC_pin_num=DEFAULT_BUTTON_C_PIN_NUM,oled_width=DEFAULT_OLED_WIDTH,oled_height=DEFAULT_OLED_HEIGHT):
  self._name=rig_name
  self._id=hexlify(unique_id()).decode("utf-8")
  self._i2c_scl_pin_num=i2c_scl_pin_num
  self._i2c_scl_pin=Pin(self.i2c_scl_pin_num)
  self._i2c_sda_pin_num=i2c_sda_pin_num
  self._i2c_sda_pin=Pin(self.i2c_sda_pin_num)
  self._i2c_freq=i2c_freq
  self._i2c=I2C(scl=self.i2c_scl_pin,sda=self.i2c_sda_pin,freq=self.i2c_freq)
  self._i2c_adapter=I2CAdapter(scl=self.i2c_scl_pin,sda=self.i2c_sda_pin,freq=self.i2c_freq)
  self._spis=dict()
  self._has_oled_board=has_oled_board
  self._oled_width=oled_width
  self._oled_height=oled_height
  if self.has_oled_board:
   self._btnA_pin_num=btnA_pin_num
   self._btnA=Pin(self.btnA_pin_num,Pin.IN)
   self._btnB_pin_num=btnB_pin_num
   self._btnB=Pin(self.btnB_pin_num,Pin.IN)
   self._btnC_pin_num=btnC_pin_num
   self._btnC=Pin(self.btnC_pin_num,Pin.IN)
   self._oled=SSD1306(self.oled_width,self.oled_height,self.i2c)
  else:
   self._btnA_pin_num=None
   self._btnA=None
   self._btnB_pin_num=None
   self._btnB=None
   self._btnC_pin_num=None
   self._btnC=None
   self._oled_width=None
   self._oled_height=None
   self._oled=None
 @property
 def name(self):
  return self._name
 @name.setter
 def name(self,value):
  self._name=value
 @property
 def id(self):
  return self._id
 @property
 def name_len(self):
  return len(self._name)
 @property
 def i2c_scl_pin_num(self):
  return self._i2c_scl_pin_num
 @property
 def i2c_scl_pin(self):
  return self._i2c_scl_pin
 @property
 def i2c_sda_pin_num(self):
  return self._i2c_sda_pin_num
 @property
 def i2c_sda_pin(self):
  return self._i2c_sda_pin
 @property
 def i2c_freq(self):
  return self._i2c_freq
 @property
 def i2c(self):
  return self._i2c
 @property
 def i2c_adapter(self):
  return self._i2c_adapter
 def get_i2c_device(self,device_address):
  return I2CDevice(self.i2c,device_address)
 def get_spi(self,id=HSPI,sck=Pin(DEFAULT_SPI_SCK_PIN_NUM),mosi=Pin(DEFAULT_SPI_MOSI_PIN_NUM),miso=Pin(DEFAULT_SPI_MISO_PIN_NUM),baudrate=DEFAULT_SPI_FREQUENCY,polarity=DEFAULT_SPI_POLARITY,phase=DEFAULT_SPI_PHASE,bits=DEFAULT_SPI_BITS,firstbit=DEFAULT_SPI_FIRST_BIT):
  if not id in self._spis:
   self._spis[id]=SPI(id,baudrate=baudrate,polarity=polarity,phase=phase,bits=bits,firstbit=firstbit,sck=sck,mosi=mosi,miso=miso)
  return self._spis[id]
 def has_oled_board(self):
  return self._has_oled_board
 @property
 def btnA_pin_num(self):
  return self._btnA_pin_num
 @property
 def btnA(self):
  return self._btnA
 def btnA_pressed(self):
  return self.btnA and not self.btnA.value()
 @property
 def btnB_pin_num(self):
  return self._btnB_pin_num
 @property
 def btnB(self):
  return self._btnB
 def btnB_pressed(self):
  return self.btnB and not self.btnB.value()
 @property
 def btnC_pin_num(self):
  return self._btnC_pin_num
 @property
 def btnC(self):
  return self._btnC 
 def btnC_pressed(self):
  return self.btnC and not self.btnC.value()
 @property
 def oled_width(self):
  return self._oled_width
 @property
 def oled_height(self):
  return self._oled_height
 @property
 def oled(self):
  return self._oled
 def deinit(self):
  for id,spi in self._spis.items():
   spi.deinit()
  if self.oled:
   self.oled.fill(0)
   self.oled.show()
