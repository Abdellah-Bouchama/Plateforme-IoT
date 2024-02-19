from lib.bluetooth_manager import BluetoothManager
import lib.bluetooth_manager as BTMANAGER
from lib.wifi_manager import WifiManager



import lib.config as configuration
import lib.uping as ping


import sys
import _thread
import time




try : 

    wm = WifiManager(ssid="OPPO", password="123456789azerty")
    wm.ap_broadcast()
    wm.ipV4_config("192.168.4.1", "255.255.255.0", "192.168.4.1", "192.168.4.1")
    print("\n Network information:{}".format(wm.wlan_ap.ifconfig()))
    ping.ping("192.168.4.1")
    print('starting thread for sockets')
    _thread.start_new_thread(wm.open_socket, ('192.168.4.1',))
    print("----------Thread started and continueing going to bluetooth--------------")
    time.sleep(30)
    #blue = BluetoothManager(mode=BTMANAGER.BT_SERVER_MODE)

except KeyboardInterrupt:
    print('Interrepted by keyboard')
except Exception as e:
    print('Another Exception given by {}'.format(e))
    print(sys.exc_info()[2])
