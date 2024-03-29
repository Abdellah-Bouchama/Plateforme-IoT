import network


import socket
import sys
import lib.config as configuration
from lib.pytrack import Pytrack

import time



from machine import RTC, SD
from lib.L76GNSS import L76GNSS #Localsiation 
from lib.LIS2HH12 import LIS2HH12 #Accelerometre
from lib.pycoproc_2 import Pycoproc
from lib.wifi_manager import WifiManager
from lib.bluetooth_manager import BluetoothManager
import lib.bluetooth_manager as BTMANAGER


node_ip = "10.2.29.150"
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
    #wlan_sta = network.WLAN(mode=network.WLAN.STA)
    #wm = WifiManager(ssid = 'WifiManager', password = 'wifimanager')
    #wm.wifi_connect('OPPO Reno10 5G', 'r3nfqaz6')
    #wm.ipV4_config(setup.ip_address, configuration.NET_MASK, configuration.GATEWAY, configuration.DNS_SERVER)
    #print('After config {}'.format(wm.get_address()))
    #wm.ap_broadcast()
    #wm.check_status()

    blue = BluetoothManager(mode=BTMANAGER.BT_SERVER_MODE)
  



    #bt_adv = BluetoothManager()
    #bt_adv.scan_devices(100)
    #bt_adv.advertise()

except KeyboardInterrupt:
    print('Interrepted by keyboard')
except Exception as e:
    print('Another Exception given by {}'.format(e))
    print(sys.exc_info()[2])