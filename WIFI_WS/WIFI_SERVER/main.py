import network


import socket
import _thread
import sys
import lib.config as configuration
from lib.pytrack import Pytrack

import time



from machine import RTC, SD
from lib.L76GNSS import L76GNSS #Localsiation 
from lib.LIS2HH12 import LIS2HH12 #Accelerometre
from lib.pycoproc_2 import Pycoproc
from lib.wifi_manager import WifiManager
import lib.uping as ping
from lib.mqtt import MQTTClient

node_ip = "10.2.18.125"
setup = configuration.Configure(node_ip)





#--------------------Accelerometre-----------------------#
# acc = LIS2HH12()
# try :
#     while True:
#         pycom.rgbled(0xFF0000)  # Red : Pitch Reading
#         print('This is the pitch : {}'.format(acc.pitch()))
#         time.sleep(1)
        
#         pycom.rgbled(0x0000FF)  # Blue : Roll Reading
#         print('This is the roll : {}'.format(acc.roll()))
#         time.sleep(1)

#         pycom.rgbled(0x00FF00)  # Green : GPS Reading
#         coord = l76.coordinates()
#         print("These are coordinates : {}".format(coord, gc.mem_free()))

#         time.sleep(1)

#--------------------End Accelerometre-----------------------#

try : 

    wm = WifiManager(ssid="OPPO", password="123456789azerty")
    wm.ap_broadcast()
    wm.ipV4_config("192.168.4.1", "255.255.255.0", "192.168.4.1", "192.168.4.1")
    print("\n Network information:{}".format(wm.wlan_ap.ifconfig()))
    ping.ping("192.168.4.1")
    print('starting thread for sockets')
    _thread.start_new_thread(wm.open_socket, ('192.168.4.1',))
    print("----------Thread started and continueing going to bluetooth--------------")

    

except KeyboardInterrupt:
    print('Interrepted by keyboard')
except Exception as e:
    print('Another Exception given by {}'.format(e))
    print(sys.exc_info()[2])