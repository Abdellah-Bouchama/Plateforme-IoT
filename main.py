import machine
import math
import network
import os
import pycom
import time, utime
import socket
import struct, ubinascii
import gc
import sys



from machine import RTC, SD
from lib.L76GNSS import L76GNSS #Localsiation 
from lib.LIS2HH12 import LIS2HH12 #Accelerometre
from lib.pycoproc_2 import Pycoproc
from lib.wifi_manager import WifiManager
from lib.bluetooth_manager import BluetoothManager

#Initialisation 
pycom.heartbeat(False)
pycom.rgbled(0x0A0A08)

gc.enable() #Enabeling the garbage collector

#RTC setting
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print("\n RTC set from NTP to UTC : {}".format(rtc.now()))
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')
print('Device MAC adress :',ubinascii.hexlify(machine.unique_id()))




#Device check
py = Pycoproc()
if py.read_product_id() != Pycoproc.USB_PID_PYTRACK:
    raise Exception("This device is not a pytrack !!")

# l76 = L76GNSS(py, timeout=30, buffer=512)

# pybates_enabled = False
# if 'pybytes' in globals():
#     print("pybytes found !!")
#     if (pybytes.isconnected()):
#         print('pybytes is connected')
#         pybates_enabled = True

# else :
#     print("pybytes not found !!")

""" 
    Attention : Pybytes is not found
"""


"""
    Add coordinates storage on SD
"""

#------------------WIFI----------------------#
# SSID = 'HUAWEI P30'

# wlanSTA = network.WLAN(mode=network.WLAN.STA)
# wlanSTA.connect(SSID, auth=(network.WLAN.WPA2, 'abd12345678'))
# timeout = time.time() + 5 # Wait 30 seconds for connexion binding
# while not wlanSTA.isconnected():
#     if time.time()> timeout :
#         break
#     time.sleep_ms(500)
#     print("Waiting for connection to wifi")

# if wlanSTA.isconnected():
#     print("we are connected to wifi {}".format(SSID))
#     print("confirguration \n", wlanSTA.ifconfig())

# #Create an access point 
# AP_SSID = "FiPyAP "
# AP_password = "12345678"
# wlanAP = network.WLAN(network.WLAN.AP)
# wlanAP.init(mode =network.WLAN.AP, ssid =AP_SSID, auth = (network.WLAN.WPA2, AP_password))
# #Waiting for clients to be connected on the AP

# while not ap.isconnected():
#     print("Actvating {} access point on the fipy please wait".format(AP_SSID))

# time.sleep_ms(3)
# print("Braodcasting AP signal on {}".format(AP_SSID))
# print(wlanAP.ifconfig())


#--------------------Connecting to a bluetooth boradcaster-------------------------#

# bt = network.Bluetooth()
# bt.start_scan(-1)

# try :
#     print("Detecting nearby bleutooth networks")
#     while True :
#         adv = bt.get_adv()
#         if adv : 
#             name = bt.resolve_adv_data(adv.data, network.Bluetooth.ADV_NAME_CMPL)
            
#             if name!= None:
#                 print('adv name',name )
#                 time.sleep(3)
#         if adv and bt.resolve_adv_data(adv.data, network.Bluetooth.ADV_NAME_CMPL) =='OPPO Reno10 5G':
#             print('if')
#             rssi = adv.rssi
#             print("RSSI : {}".format(rssi))
# except KeyboardInterrupt:
#     print('Interrepted')
# except Exception as e:
#     print('Another Exception {}'.format(e))



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

try : 
    wlan_sta = network.WLAN(mode=network.WLAN.STA)
    wm = WifiManager()
    wm.wifi_connect('OPPO Reno10 5G', 'r3nfqaz6')
    wm.ipV4_config('192.168.46.88', '255.255.255.0', '192.168.46.216', '192.168.46.216')
    print('After config {}'.format(wm.get_address()))
    wm.check_status()


    bt_adv = BluetoothManager()
    bt_adv.scan_devices(100)
    #bt_adv.advertise()

except KeyboardInterrupt:
    print('Interrepted')
except Exception as e:
    print('Another Exception {}'.format(e))
    print(sys.exc_info()[2])