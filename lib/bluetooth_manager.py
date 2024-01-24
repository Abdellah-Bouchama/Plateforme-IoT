from network import Bluetooth
import ubinascii


import lib.logging as logger
import time



class BluetoothManager:

    def __init__(self, mode = 'Advertizer') :

        self.bt = Bluetooth()
        self.mode = mode
        self.logger = logger


        if mode == 'Advertizer' :
            self.advertise()

        if mode == 'client' :
            self.scan_devices()
            
        # srv1 = self.bt.service(uuid=0xec00, isprimary=True,nbr_chars=1)
        # chr1 = srv1.characteristic(uuid=0xec0e, value='read_from_here') #client reads from here
        # chr1.callback(trigger=Bluetooth.CHAR_READ_EVENT, handler=self.chr1_handler)  # Déclencheur pour l'événement de lecture
        # chr1.callback(trigger=Bluetooth.CHAR_SUBSCRIBE_EVENT, handler=self.chr1_handler)  # Déclencheur pour l'événement de souscription
        # chr1.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_SUBSCRIBE_EVENT), handler=self.chr1_handler)

    def advertise(self,name = "FiPy", password = "1234567890"):
        self.bt.set_advertisement(name='1', manufacturer_data="Pycom", service_uuid=0xec00)
        self.bt.callback(trigger=self.bt.CLIENT_CONNECTED | self.bt.CLIENT_DISCONNECTED, handler=self.connexion_callback)
        self.bt.advertise(True)

    def scan_devices(self):

        bt = Bluetooth()
        bt.start_scan(-1)

        try :
            print("Detecting nearby bleutooth networks")
            while True :
                adv = bt.get_adv()
                if adv : 
                    name = bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL)
                    
                    if name!= None:
                        print('adv name',name )
                        time.sleep(3)
                if adv and bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) =='OPPO Reno10 5G':
                    print('if')
                    rssi = adv.rssi
                    print("RSSI : {}".format(rssi))
        except KeyboardInterrupt:
            print('Interrepted')
        except Exception as e:
            print('Another Exception {}'.format(e))


        # while True:
        #     print(self.bt.get_adv())
        #     time.sleep(3)


        # self.bt.start_scan(time)
        # print("Detecting nearby bleutooth networks")
        # logger.info("Detecting nearby bleutooth networks")
        # while self.bt.isscanning():
        #     adv = self.bt.get_adv()
        #     if adv:
        #         # try to get the complete name
        #         name = self.bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL)
        #         if name!= None:
        #             print('adv name',name )
        #             time.sleep(1)
        #             mfg_data = self.bt.resolve_adv_data(adv.data, Bluetooth.ADV_MANUFACTURER_DATA)

        #             if mfg_data:
        #                 # try to get the manufacturer data (Apple's iBeacon data is sent here)
        #                 print(ubinascii.hexlify(mfg_data))

    

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



        
