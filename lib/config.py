import pycom
import machine
import time, utime
import logging
import gc
from lib.pycoproc_2 import Pycoproc
from micropython import const
import ubinascii





NTP_SERVER = "pool.ntp.org" # Or 10.12.10.134
WIFI_SSID = "dragino-227e3c"
WIFI_PW = "dragino+dragino"
SERVER_IP = "10.2.30.158"
NET_MASK = "255.255.0.0"
GATEWAY = "10.2.1.1"
DNS_SERVER = "10.2.1.1"



class Configure :



    def __init__(self, ip_address):

        self.logger = logging
        self.logger.basicConfig(level=logging.INFO)
        self.ip_address = ip_address 

        #Printing MAC and ip addresses to identify
        self.logger.info("This device MAC address is {}".format(ubinascii.hexlify(machine.unique_id(),':').decode()))
        self.logger.info("This device IP address is {}".format(self.ip_address))

        #Initialisation 
        pycom.heartbeat(False)
        pycom.rgbled(0x0A0A08)

        #Enabeling the garbage collector
        gc.enable() 

        #RTC setting
        rtc = machine.RTC()
        self.logger.info("Syncing to NTP server {}".format(NTP_SERVER))
        rtc.ntp_sync(NTP_SERVER)
        utime.sleep_ms(750)
        print("\n RTC set from NTP to UTC : {}".format(rtc.now()))

        #Device check
        py = Pycoproc()
        if py.read_product_id() != Pycoproc.USB_PID_PYTRACK:
            self.logger.CRITICAL("This device was not recognized as a Pytrack device")
            raise Exception("This device is not a pytrack device!!")