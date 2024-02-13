from network import Bluetooth
from machine import Timer
import ubinascii
import LIS2HH12

import _thread



import lib.logging as logger
import lib.setup as setup
import time


BTBIND_PERIOD = const(10)
BTSCAN_PERIOD = const(10)
BTBIND_RETRY = const(4)

BT_CLIENT_MODE = 'CLIENT'
BT_SERVER_MODE = 'ADVERTIZER'
battery = 100
update = False
class BluetoothManager:

    def __init__(self, mode = BT_CLIENT_MODE) :

        self.bt = Bluetooth()
        self.mode = mode
        self.logger = logger
        self.adv_dict = {}
        self.conn = None
        self.chr1 = None


        if mode == BT_SERVER_MODE :
            self.advertise()

        if mode == BT_CLIENT_MODE :
            self.scan_devices()
            self.bind("FiPy 45")
            self.read_data()


    def scan_devices(self):

        self.bt.start_scan(-1)

        try :
            print("Detecting nearby bleutooth networks")
            scanning_deadline = time.time() + BTBIND_PERIOD
            while time.time() < scanning_deadline :
                adv = self.bt.get_adv()
                if adv : 
                    name = self.bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL)
                    if name!= None and name not in self.adv_dict:
                        print('advertizer name',name )
                        self.adv_dict[name] = adv

            self.logger.info("Found pairs : {}".format(self.adv_dict))
        except KeyboardInterrupt:
            print('Interrepted')
        except Exception as e:
            print('Another Exception {}'.format(e))

    
    def bind(self, adv_name : str):
        waiting_deadline = time.time() + BTBIND_PERIOD
        while time.time() < waiting_deadline :
            for advertizer in self.adv_dict.keys() :
                #advertizer_name = self.bt.resolve_adv_data(advertizer.data, Bluetooth.ADV_NAME_CMPL)
                if advertizer == adv_name:
                    select_adv = self.adv_dict[advertizer]
                    break
            print(self.adv_dict, select_adv)
            try :

                self.conn = self.bt.connect(select_adv.mac)  
                print("Connected to device {} with mac addresse = {}".format(adv_name, ubinascii.hexlify(select_adv.mac)))  
                _thread.start_new_thread(setup._setblueledblink, (0.3))
                break
            except KeyboardInterrupt:
                print('Interrepted by keyboard')   
            except Exception as e:
                print('Exception is {}'.format(e))
                self.logger.warning("Could not bind ... rebinding in {} seconds".format(BTBIND_RETRY))
                time.sleep(5)

        print('end of bind')
        
        

    def read_data(self):

        print('start of read')
        try:
            services = self.conn.services()
            for service in services:
                chars = service.characteristics()
                for char in chars:
                    c_uuid = char.uuid()
                    if c_uuid == 0xec0e:
                        if (char.properties() & Bluetooth.PROP_NOTIFY):
                            char.callback(trigger=Bluetooth.CHAR_NOTIFY_EVENT, handler=self.char_notify_callback)
                            print(c_uuid)
                            break
        except Exception as e:
            print("Read exception : {}.".format(e))
                

    def char_notify_callback(self, char, arg):
        char_value = (char.value())
        print("New value: {}".format(char_value))


    def connexion_callback (self, bt_o):
        events = bt_o.events()   # this method returns the flags and clears the internal registry
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            logger.info("Client Connected")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")
            logger.warning("Client disconnected")

    def chr1_handler(self, chr, data):
        global battery
        global update
        events = chr.events()
        print("events: ",events)
        if events & (Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT):
            chr.value(battery)
            print("transmitted :", battery)
            if (events & Bluetooth.CHAR_SUBSCRIBE_EVENT):
                update = True

    def update_handler(self, update_alarm):
        global battery
        global update
        battery-=1
        if battery == 1:
            battery = 100
        if update:
            self.chr1.value(str(battery))



    def advertise(self) : 

        self.bt.set_advertisement(name='FiPy 45', manufacturer_data="Pycom", service_uuid=0xec00)

        self.bt.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.connexion_callback)
        self.bt.advertise(True)

        srv1 = self.bt.service(uuid=0xec00, isprimary=True,nbr_chars=1)

        self.chr1 = srv1.characteristic(uuid=0xec0e, value='read_from_here') #client reads from here

        self.chr1.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=self.chr1_handler)
        print('Start BLE service')

        update_alarm = Timer.Alarm(self.update_handler, 1, periodic=True)
            

    
    #Disconect as client from the bluetooth broadcaster
    def disconnect_binding(self):

        self.conn.disconnect()

    #Disconnect all client as a bluetooth broadcaster
    def disconnect_clients(self):

        self.bt.disconnect()

    #Turn bluetooth off
    def turn_off(self):

        self.bt.deinit()

    def show_adv_info(self, adv):

        rssi = adv.rssi
        mfg_data = self.bt.resolve_adv_data(adv.data, Bluetooth.ADV_MANUFACTURER_DATA)
        mac = adv.mac

        print("Manufacturer data : {}".format(ubinascii.hexlify(mfg_data)))
        print("RSSI : {}".format(rssi)) 

