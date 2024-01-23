from network import Bluetooth
import ubinascii


import lib.logging as logger



class BluetoothManager:

    def __init__(self, mode = 'Advertizer') :

        self.bt = Bluetooth()
        self.mode = mode


        self.logger = logger


    def scan_devices(self, time):

        self.bt.start_scan(time)
        print("Detecting nearby bleutooth networks")
        logger.info("Detecting nearby bleutooth networks")
        while self.bt.isscanning():
            adv = self.bt.get_adv()
            if adv:
                # try to get the complete name
                name = self.bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL)
                if name!= None:
                    print('adv name',name )
                    time.sleep(1)
                    mfg_data = self.bt.resolve_adv_data(adv.data, Bluetooth.ADV_MANUFACTURER_DATA)

                    if mfg_data:
                        # try to get the manufacturer data (Apple's iBeacon data is sent here)
                        print(ubinascii.hexlify(mfg_data))

    def advertise(self,name = "FiPy", password = "1234567890"):
        self.bt.set_advertisement(name=name, service_uuid=b'1234567890123456')
        self.bt.callback(trigger=self.bt.CLIENT_CONNECTED | self.bt.CLIENT_DISCONNECTED, handler=self.connexion_callback)
        self.bt.advertise(True)

    def connexion_callback (self, bt_o):
        events = bt_o.events()   # this method returns the flags and clears the internal registry
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            logger.info("Client Connected")
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")
            logger.warning("Client disconnected")







    def disconnect(self):

        self.bt.deinit()



        
