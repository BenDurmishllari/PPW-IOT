# File: file_write_pub.py
# Description: Sample code for PPW1 script to run on the IoT Prototype Rig
# Author: Arben Durmishllari, University of Sunderland
# Date: May 2019

# Imports
import random
import os
from time import sleep
from libs.iot_app import IoTApp
from libs.bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, ENABLE_GAS_MEAS
from neopixel import NeoPixel
from machine import Pin

# Classes
class MainApp(IoTApp):
    """
    This is your custom class that is instantiated as the main app object instance,
    it inherits from the supplied IoTApp class found in the libs/iot_app.py module
    which is copied when the Huzzah32 is prepared.
    This IoTApp in turn encapsulates an instance of the ProtoRig class (which is 
    found in libs/proto_rig.py) and exposes a number of properties of this ProtoRig
    instance so you do not have to do this yourself.
    Also, the IoTApp provides an execution loop that can be started by calling the
    run() method of the IoTApp class (which is of course inherited into your custom
    app class). All you have to do is define your program by providing implementations
    of the init(), loop() and deinit() methods.
    Looping of your program can be controlled using the finished flag property of
    your custom class.
    """

    AP_SSID = "DCETLocalVOIP"
    AP_PSWD = ""
    AP_TOUT = 5000
    MQTT_ADDR = "192.168.2.138"  # Your desktop PC Wi-Fi dongle IP address
    MQTT_PORT = 1883
    # Literal string values can be converted to binary representation by using a b prefix
    MQTT_TEST_TOPIC_1 = b"cet235/test/ticks"
    MQTT_TEST_TOPIC_2 = b"cet235/test/secs"


    def init(self):
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
        self.message = "None"
        self.gap = " "
        self.active = False
        self.topic_1_count = 0
        self.topic_1_colour = 0
        
        self.wifi_msg = "No WIFI"
        connect_count = 0
        # Try to connect to WiFi 5 times, if unsuccessful then only try again if button A on
        # the OLED is pressed
        while connect_count < 5 and not self.is_wifi_connected():
            self.oled_clear()
            self.wifi_msg = "Connect WIFI:{0}".format(connect_count + 1) 
            self.oled_text(self.wifi_msg, 0, 0)
            self.oled_display()
            self.connect_to_wifi(wifi_settings=(self.AP_SSID, self.AP_PSWD, True, self.AP_TOUT))
            connect_count += 1

        if self.is_wifi_connected():
            self.wifi_msg = "WIFI"
            # Register with the MQTT broker and link the method mqtt_callback() as the callback
            # when messages are recieved
            self.register_to_mqtt(server=self.MQTT_ADDR, port=self.MQTT_PORT,
                                  sub_callback=self.mqtt_callback)
            # Subscribe to topic "cet235/test/ticks"
            self.mqtt_client.subscribe(self.MQTT_TEST_TOPIC_1)

            # Subscribe to topic "cet235/test/secs"
            self.mqtt_client.subscribe(self.MQTT_TEST_TOPIC_2)

            self.oled_clear()
            self.oled_display()
        else:
            self.wifi_msg = "No WIFI"
            self.oled_clear()
            self.oled_display()




 
        self.neopixel_pin = self.rig.PIN_21
        
        # Set pin 21 to be a digital output pin that is initially pulled down (off)
        self.neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)
       
        self.npm = NeoPixel(self.neopixel_pin, 32, bpp=3, timing=1)

        
        self.rtc.datetime((2019, 3, 5, 1, 9, 0, 0, 0))
        
        # Instantiate a BME680 object and configure it using the obtain_sensor_bme680()
        # method
        self.obtain_sensor_bme680()
        
        # Name of the file to write to the Huzzah32's root file system
        self.file_name = "access_data.csv"
        
       
        if self.file_exists(self.file_name):
            os.remove(self.file_name)
        
        
        self.file = open(self.file_name, "w+")
        
        
        self.access = False
        self.access_str = ""
        
        # counts variables 
        self.count = 0
        self.lightcount=0

        
        self.npm.fill((5,5,5))
        self.npm.write()
        
        self.npm.write()

    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        
      
        if self.is_wifi_connected():
            # Check for any messages received from the MQTT broker, note this is a non-blocking
            # operation so if no messages are currently present the loop() method continues
            self.mqtt_client.check_msg()
        
   

        # If sensor readings are available, read them once a second or so
        if self.sensor_bme680.get_sensor_data():
            tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius 
            rh_reading = self.sensor_bme680.data.humidity     # As a percentage (ie. relative humidity)
                
            # Current date and time taken from the real-time clock
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]

            
            if self.access:
                
                if self.count == 0:
                    date_str = "{0}/{1}/{2}".format(day, month, year)
                    time_str = "{0}:{1}:{2}".format(hour, minute, second)

                    # Write to file
                    self.file.write("{0},{1},{2} \n".format("ACCESS-STARTED", date_str ,time_str))

                # Format timestamp
                
                timestamp = "{0}-{1}-{2}|{3}:{4}:{5}".format(year, month, day, hour, minute, second)

                # Format line of data
                data_line = "{0},{1:.2f},{2:.2f},{3}\n".format(timestamp, tm_reading, rh_reading,self.message)
            
                # Write data line to the access_data.csv file
                if self.message != "None":
                    self.file.write(data_line)
                
                
                # Set correct colour for NeoPixel matrix LEDS and correct access warning string
                if self.lightcount==0:
                    self.npm.fill((0, 0, 0))
                    self.npm.write()
                elif self.lightcount <=5 :
                    self.npm.fill((0, 10, 0))
                    self.npm.write()
                elif self.lightcount > 5 and self.lightcount <=10:
                    self.npm.fill((10, 10, 0))
                    self.npm.write()
                elif self.lightcount > 10:
                    self.npm.fill((10, 0, 0))
                    self.npm.write()
                # Increment seconds counter
                self.count += 1
                self.lightcount +=0.10

                
     
    
    def mqtt_callback(self, topic, msg):
        
        topic = self.MQTT_TEST_TOPIC_2
            
            # self.oled_fill(24, 8, 80, 16, self.oled_background)


        sleep(1)

        self.message = (str(bytes(msg), "utf-8"))
            
        if (self.message != "None"):
            self.oled_clear()
            self.oled_text("Employee: ",0,0)
            self.oled_text("on room: ",0,10)
            self.oled_text(self.message,0,20)
            self.access = True
            self.oled_display()
            
        else :
            self.lightcount = 0
            self.oled_clear()
            self.oled_text("Employee: ",0,0)
            self.oled_text("on room: ",0,10)
            self.oled_text(self.message,0,20)
            self.oled_display()
            #self.active = True







    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # Clear the NeoPixel matrix
        self.npm.fill((0, 0, 0))
        self.npm.write()

        # If an access period is currently active then write to the access_data.csv file that it
        # is now stopped and also the length of the access period in seconds
        if self.access:
            # Current date and time taken from the real-time clock to record as stop date and time
            # for this access period
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]
            
            date_str = "{0}/{1}/{2}".format(day, month, year)
            time_str = "{0}:{1}:{2}".format(hour, minute, second)

            # Write to file, note: self.count is approximately the number of seconds that this access
            # period lasted
            self.file.write("{0},{1},{2},{3}\n".format("ACCESS-STOPPED", date_str, time_str ,self.count))

        # Make sure the access_data.csv file is closed
        self.file.close()
        
    def obtain_sensor_bme680(self):

        self.sensor_bme680 = BME680(i2c=self.rig.i2c_adapter, i2c_addr = 0x76)
        self.sensor_bme680.set_temperature_oversample(OS_8X)
        self.sensor_bme680.set_humidity_oversample(OS_2X)
        self.sensor_bme680.set_filter(FILTER_SIZE_3)
        
    def file_exists(self, file_name):
        file_names = os.listdir()

        return file_name in file_names

    def btnA_handler(self, pin):

        if not self.access:
            # Current date and time taken from the real-time clock to record as start date and time
            # for this access period
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]
            
            date_str = "{0}/{1}/{2}".format(day, month, year)
            time_str = "{0}:{1}:{2}".format(hour, minute, second)

            # Write to file
            self.file.write("{0},{1},{2}\n".format("ACCESS-STARTED", date_str, time_str))
        
            # Update access information
            self.access = True
            self.access_str = "ACCESS"
            self.count = 0
        
    def btnB_handler(self, pin):
        if self.access:

            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]
            
            date_str = "{0}/{1}/{2}".format(day, month, year)
            time_str = "{0}:{1}:{2}".format(hour, minute, second)

            # Write to file, note: self.count is approximately the number of seconds that this access
            # period lasted
            self.file.write("{0},{1},{2},{3}\n".format("ACCESS-STOPPED", date_str, time_str, self.count))
        
            # Update access information
            self.access = False
            self.access_str = ""

            # Clear the NeoPixel matrix
            self.npm.fill((0, 0, 0))
            self.npm.write()

def main():

    app = MainApp(name="PPW1 Sample", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

if __name__ == "__main__":
    # execute only if run as a script
    main()
