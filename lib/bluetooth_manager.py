from network import Bluetooth
import ubinascii


import lib.logging as logger
import time


BTBIND_PERIOD = const(10)
BTSCAN_PERIOD = const(10)
BTBIND_RETRY = const(4)

BT_CLIENT_MODE = 'CLIENT'
BT_SERVER_MODE = 'ADVERTIZER'

class BluetoothManager:

    def __init__(self, mode = BT_CLIENT_MODE) :

        self.bt = Bluetooth()
        self.mode = mode
        self.logger = logger
        self.adv_dict = {}
        self.conn = None


        if mode == BT_SERVER_MODE :
            self.advertise()

        if mode == BT_CLIENT_MODE :
            self.scan_devices()
            
        # srv1 = self.bt.service(uuid=0xec00, isprimary=True,nbr_chars=1)
        # chr1 = srv1.characteristic(uuid=0xec0e, value='read_from_here') #client reads from here
        # chr1.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=self.chr1_handler)  # Déclencheur pour l'événement de lecture
        # chr1.callback(trigger=Bluetooth.CHAR_SUBSCRIBE_EVENT, handler=self.chr1_handler)  # Déclencheur pour l'événement de souscription
        # chr1.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=self.chr1_handler)

    # Broadcast for a bleutooth access
    def advertise(self,name = "FiPy", password = "1234567890"):
        self.bt.set_advertisement(name=name, manufacturer_data="Pycom", service_uuid=0xec00)
        self.bt.callback(trigger=self.bt.CLIENT_CONNECTED | self.bt.CLIENT_DISCONNECTED, handler=self.connexion_callback)
        self.bt.advertise(True)

    #Scan available broadcasting bluetooth devices
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


    # Connect to a Bluetooth advertizer
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
                 

                return True 
            except KeyboardInterrupt:
                print('Interrepted by keyboard')   
            except Exception as e:
                print('Exception is {}'.format(e))
                self.logger.warning("Could not bind ... rebinding in {} seconds".format(BTBIND_RETRY))
                time.sleep(5)
        
        return False
    
    def read_data(self):

        if (self.conn):

            services = self.conn.services()
            for service in services:
              time.sleep(0.050)
              if type(service.uuid()) == bytes:
                  print('Reading chars from service = {}'.format(service.uuid()))
              else:
                  print('Reading chars from service = %x' % service.uuid())
              chars = service.characteristics()
              for char in chars:
                  if (char.properties() & Bluetooth.PROP_READ):
                      print('char {} value = {}'.format(char.uuid(), char.read()))
        else :
            raise ("Could not read data, no conection found!")
    
    #Disconect as client from the bluetooth broadcaster
    def disconnect_binding(self):

        self.conn.disconnect()

    #Disconnect all client as a bluetooth broadcaster
    def disconnect_clients(self):

        self.bt.disconnect()

    def show_adv_info(self, adv):

        rssi = adv.rssi
        mfg_data = self.bt.resolve_adv_data(adv.data, Bluetooth.ADV_MANUFACTURER_DATA)
        mac = adv.mac

        print("Manufacturer data : {}".format(ubinascii.hexlify(mfg_data)))
        print("RSSI : {}".format(rssi)) 

    

    def connexion_callback (self, bt_o):
        events = bt_o.events()   # this method returns the flags and clears the internal registry
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            logger.info("Client Connected")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")
            logger.warning("Client disconnected")

    def chr1_handler(chr,data):
        global c
        global cx,n,k
        if (k==0):
            data=str(n)+"*"+"vous etes connectes"
            c=0
            k=1

        else:
            data= str(n)+"*"+"req"
            cx=1
    #if (Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT):
        chr.value(data)







    def disconnect(self):

        self.bt.deinit()



        
