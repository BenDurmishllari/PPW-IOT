# File: mfrc522_read_example.py
# Description: Example code for using the MFRC522 RFID module to read a single block 
#              from a Mifare Classic 1K card/tag
# Author: Arben Durmishllari, University of Sunderland
# Date: Jan 2019

# Imports
from libs.iot_app import IoTApp
from libs.mfrc522 import MFRC522
from time import sleep

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
    def init(self):
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
        self.rfid_device = MFRC522(sck=5, mosi=18, miso=19, rst=17, cs=16)
        
        self.address = 8
        self.read = False
        self.data = None
   
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        if not self.read:
            self.oled_clear()

            self.oled_text("Present RFID Tag", 0, 0)
            
            (self.read, msg, tag_type, raw_uid, self.data) = self.read_from_tag(self.address)

            self.oled_text(msg, 0, 10)
            self.oled_display()
        else:
            self.oled_text(str(bytes(self.data), "utf-8"), 0, 20)
            self.oled_display()
            self.address = 9
            self.read = False
            sleep(5)
            # self.finish()
    
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        if self.rfid_device:
            self.rfid_device.deinit()

    def read_from_tag(self, address, key=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]):
        rfid_device = self.rfid_device
        raw_uid = None
        data = None
        
        (status, tag_type) = rfid_device.request(rfid_device.REQIDL)

        if status == rfid_device.OK:
            (status, raw_uid) = rfid_device.anticoll()

            if status == rfid_device.OK:
                status = rfid_device.select_tag(raw_uid)
                
                if status == rfid_device.OK:
                    status = rfid_device.auth(rfid_device.AUTHENT1A, address, key, raw_uid)
                    
                    if status == rfid_device.OK:
                        data = rfid_device.read(address)
                        rfid_device.stop_crypto1()
                        return (True, "Data is read", tag_type, raw_uid, data)
                    else:
                        return (False, "Fail: Auth key", tag_type, raw_uid, data)
                else:
                    return (False, "Fail: Select tag", tag_type, raw_uid, data)
            else:
                return (False, "Fail: Anti-coll", tag_type, raw_uid, data)
        else:
            return (False, "Fail: No tag", tag_type, raw_uid, data)

# Program entrance function
def main():
    """
    Main function, this instantiates an instance fo your custom class (where you can
    initialise your custom class instance to how you wish your app to operate) and
    then executes the run() method to get the app running
    """
    # Instantiate an instance of the custom IoTApp class (MainApp class) with the following
    # property values:-
    #
    #   name: "MFRC522 Read", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="MFRC522 Read", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
