import sys
import network
import esp
import socket
import struct
from time import sleep,ticks_ms,localtime
from machine import Pin,RTC
from libs.mqtt_simple_ex import MQTTClientEx
from libs.proto_rig import ProtoRig as Rig
class RunStates:
 NOT_STARTED=1
 STARTING=2
 INITIALISING=3
 LOOPING=4
 DEINITIALISING=5
 SHUTTING_DOWN=6
class IoTApp:
 _DEFAULT_LOOP_SLEEP_TIME=0.1
 _NTP_ERROR_CODE=-1
 _NTP_QUERY=bytearray(48)
 _NTP_QUERY[0]=0x1b
 _NTP_DEFAULT_PORT=123
 _NTP_DEFAULT_TIMEOUT=1
 _NTP_DELTA=3155673600 
 _DAY_NAMES=("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
 _BST_DATES={2017:(26,29),2018:(25,28),2019:(31,27),2020:(29,25),2021:(28,31),2022:(27,30),2023:(26,29),2024:(31,27),2025:(30,26),2026:(29,25),2027:(28,31),2028:(26,29),2029:(25,28),2030:(31,27)}
 _BST_START_MN=3
 _BST_START_HR=1
 _BST_END_MN=10
 _BST_END_HR=1
 _BST_INCREMENT=3600 
 def __init__(self,name,has_oled_board=True,i2c_freq=Rig.DEFAULT_I2C_FREQUENCY,finish_button="C",start_verbose=True,apply_bst=True,debug_on=True):
  if not debug_on:
   esp.osdebug(None) 
  self.start_verbose=start_verbose
  self.apply_bst=apply_bst
  self.rig=Rig(has_oled_board=has_oled_board,i2c_freq=i2c_freq)
  self.oled_background=0
  self.oled_foreground=1
  self.oled_on=True
  if self.rig.has_oled_board():
   self.name = name if len(name) < int(14 * (self.rig.oled_width / 128)) + 1 else name[:int(14 * (self.rig.oled_width / 128)) + 1]
  else:
   self.name = name
  self.rig.name="IoTApp-[{0}]-Rig".format(self.name)
  self.finished=False
  if self.rig.has_oled_board():
   if finish_button:
    if finish_button.upper()=="A":
     self.rig.btnA.irq(self.finish_handler)
     self.rig.btnB.irq(self.btnB_handler)
     self.rig.btnC.irq(self.btnC_handler)
    elif finish_button.upper()=="B":
     self.rig.btnB.irq(self.finish_handler)
     self.rig.btnA.irq(self.btnA_handler)
     self.rig.btnC.irq(self.btnC_handler)
    elif finish_button.upper()=="C":
     self.rig.btnC.irq(self.finish_handler)
     self.rig.btnA.irq(self.btnA_handler)
     self.rig.btnB.irq(self.btnB_handler)
    else:
     self.rig.btnA.irq(self.btnA_handler)
     self.rig.btnB.irq(self.btnB_handler)
     self.rig.btnC.irq(self.btnC_handler)
   else:
    self.rig.btnA.irq(self.btnA_handler)
    self.rig.btnB.irq(self.btnB_handler)
    self.rig.btnC.irq(self.btnC_handler)
  self.wifi=None
  self.ssid=""
  self.passkey=""
  self.auto_connect=False
  self.wait_time=0
  self.rtc=RTC()
  self.mqtt_id="{0}_{1}".format("".join(self.name.split()),self.rig.id)
  self.mqtt_client=None
  self.exit_code=0
  self.run_state=RunStates.NOT_STARTED
 def connect_to_wifi(self,wifi_settings=None,connect_now=False):
  if wifi_settings:
   self.ssid,self.passkey,self.auto_connect,self.wait_time=wifi_settings
  if self.auto_connect or connect_now:
   if not self.wifi:
    self.wifi=network.WLAN(network.STA_IF)
   if not self.wifi.active():
    self.wifi.active(True)
   if self.wifi.isconnected(): 
    self.wifi.disconnect()
   if not self.wait_time>0: 
    self.wifi.connect(self.ssid,self.passkey)
    while not self.wifi.isconnected():
     sleep(0.1)
   else:
    wait_end=ticks_ms()+self.wait_time 
    self.wifi.connect(self.ssid,self.passkey)
    while not self.wifi.isconnected()and(ticks_ms()<wait_end):
     sleep(0.1)
    if not self.wifi.isconnected():
     self.wifi.active(False) 
 def run(self):
  try:
   self.run_state=RunStates.STARTING
   self.startup()
   self.run_state=RunStates.INITIALISING
   self.init()
   self.run_state=RunStates.LOOPING
   while not self.finished:
    self.loop()
   self.run_state=RunStates.DEINITIALISING
   self.deinit()
   self.run_state=RunStates.SHUTTING_DOWN
   self.shutdown()
  except Exception as ex:
   sys.print_exception(ex)
   self.exit_code=self.run_state
   if self.run_state<RunStates.SHUTTING_DOWN:
    self.rig.deinit()
    print("\nTerminated with code: {0} <ERROR>".format(self.exit_code))
 def startup(self):
  if self.rig.has_oled_board():
   if self.start_verbose:
    self.oled_clear()
    self.oled_fill(0,0,self.rig.oled_width-1,9,1) 
    self.oled_text("Device: {0}".format(sys.platform.upper()),0,1,0)
    self.oled_text("{0}".format(sys.implementation[0]),0,10)
    self.oled_text("ver{0}.{1}.{2}".format(sys.implementation[1][0],sys.implementation[1][1],sys.implementation[1][2]),0,20)
    self.oled_display()
    sleep(1)
    self.oled_invert()
    self.oled_clear()
    self.oled_vline(((self.rig.oled_width-(len(self.name)*8))//2)-3,10,12)
    self.oled_hline(((self.rig.oled_width-(len(self.name)*8))//2)-3,10,(len(self.name)*8)+5)
    self.oled_vline(((self.rig.oled_width-(len(self.name)*8))//2)+(len(self.name)*8)+2,10,12)
    self.oled_hline(((self.rig.oled_width-(len(self.name)*8))//2)-3,21,(len(self.name)*8)+5)
    self.oled_text(self.name,(self.rig.oled_width-(len(self.name)*8))//2,12)
    self.oled_invert()
    self.oled_display()
    sleep(1)
   else:
    self.oled_clear()
    self.oled_display()
 def finish_handler(self,pin):
  self.finish()
 def finish(self):
  self.finished=True
 def oled_switch_on(self):
  self.oled_on=True
 def oled_switch_off(self):
  self.oled_on=False
 def oled_toggle(self):
  self.oled_on=not self.oled_on
 def oled_invert(self):
  if self.rig.has_oled_board()and self.oled_on:
   self.oled_background=0 if self.oled_background else 1
   self.oled_foreground=0 if self.oled_foreground else 1
 def oled_display(self):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.show()
 def oled_clear(self,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.fill(self.oled_background if colour==None else int(colour>0))
 def oled_pixel(self,x,y,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.pixel(x,y,self.oled_foreground if colour==None else int(colour>0))
 def oled_fill(self,x,y,w,h,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.fill_rect(x,y,w,h,self.oled_foreground if colour==None else int(colour>0))
 def oled_rect(self,x,y,w,h,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.rect(x,y,w,h,self.oled_foreground if colour==None else int(colour>0))
 def oled_hline(self,x,y,w,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.hline(x,y,w,self.oled_foreground if colour==None else int(colour>0))
 def oled_vline(self,x,y,h,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.vline(x,y,h,self.oled_foreground if colour==None else int(colour>0))
 def oled_line(self,x0,y0,x1,y1,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.line(x0,y0,x1,y1,self.oled_foreground if colour==None else int(colour>0))
 def oled_text(self,text,x,y,colour=None):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.text(text,x,y,self.oled_foreground if colour==None else int(colour>0))
 def oled_scroll(self,dx=0,dy=0):
  if self.rig.has_oled_board()and self.oled_on:
   self.rig.oled.scroll(dx,dy)
 def btnA_handler(self,pin):
  pass
 def btnB_handler(self,pin):
  pass
 def btnC_handler(self,pin):
  pass
 def is_wifi_connected(self):
  if self.wifi:
   return self.wifi.isconnected()
  return False
 def wifi_activate(self):
  if self.wifi:
   self.wifi.active(True)
 def wifi_deactivate(self):
  if self.wifi:
   if self.wifi.isconnected():
    self.wifi.disconnect()
    self.wifi.active(False)
 def get_ntp_datetime(self,ntp_ip,ntp_port=_NTP_DEFAULT_PORT,ntp_timeout=_NTP_DEFAULT_TIMEOUT):
  msg=None
  try:
   addr=socket.getaddrinfo(ntp_ip,ntp_port)[0][-1]
   s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
   s.settimeout(ntp_timeout)
   res=s.sendto(self._NTP_QUERY,addr)
   msg=s.recv(48)
  except:
   pass
  finally:
   s.close()
  return(struct.unpack("!I",msg[40:44])[0]-self._NTP_DELTA)if msg else self._NTP_ERROR_CODE
 def _set_rtc(self,ntp_ip=None,ntp_port=_NTP_DEFAULT_PORT,ntp_timeout=_NTP_DEFAULT_TIMEOUT,datetime=(2000,1,1,0,0,0,0,0)):
  if ntp_ip:
   t=self.get_ntp_datetime(ntp_ip,ntp_port,ntp_timeout)
   if not(t<0):
    tm=localtime(t)
    if self.apply_bst:
     add_hour=True
     mn=tm[1]
     if mn<self._BST_START_MN or mn>self._BST_END_MN:
      add_hour=False
     elif mn==self._BST_START_MN:
      yr=tm[0]
      dn=tm[2]
      hr=tm[3]
      sdn=self._BST_DATES[yr][0]
      if dn<sdn:
       add_hour=False
      elif dn==sdn:
       add_hour=hr>=self._BST_START_HR
     elif mn==self._BST_END_MN:
      yr=tm[0]
      dn=tm[2]
      hr=tm[3]
      edn=self._BST_DATES[yr][1]
      if dn>edn:
       add_hour=False
      elif dn==edn:
       add_hour=hr<self._BST_END_HR
     if add_hour:
      tm=localtime(t+self._BST_INCREMENT)
    tm=tm[0:3]+(0,)+tm[3:6]+(0,)
    self.rtc.datetime(tm)
    return True
   return False
  self.rtc.datetime(datetime) 
  return True
 def set_rtc_by_ntp(self,ntp_ip,ntp_port,ntp_timeout=_NTP_DEFAULT_TIMEOUT):
  return self._set_rtc(ntp_ip,ntp_port,ntp_timeout)
 def set_rtc_by_datetime(self,datetime):
  return self._set_rtc(datetime=datetime)
 def reset_rtc(self):
  return self._set_rtc()
 def register_to_mqtt(self,server,port=0,last_will=None,sub_callback=None,user=None,password=None,keepalive=0,ssl=False,ssl_params={}):
  self.mqtt_client=MQTTClientEx(client_id=self.mqtt_id,server=server,port=port,user=user,password=password,keepalive=keepalive,ssl=ssl,ssl_params=ssl_params)
  if last_will:
   topic,msg=last_will
   self.mqtt_client.set_last_will(topic,msg)
  if sub_callback:
   self.mqtt_client.set_callback(sub_callback)
  self.mqtt_client.connect()
 def init(self):
  pass
 def loop(self):
  pass
 def deinit(self):
  pass
 def shutdown(self):
  if self.mqtt_client:
   self.mqtt_client.disconnect()
  if self.wifi:
   if self.wifi.isconnected():
    self.wifi.disconnect()
   self.wifi.active(False)
  self.rig.deinit()
  esp.osdebug(0)
  print("\nTerminated with code: {0} <OK>".format(self.exit_code))
