import pycom, time; pycom.heartbeat(False)

#colors define
red=0x7f0000
green=0x007f00 
orange=0xff5100
blue=0x00007f
off=0x000000
white=0x7f7f7f
magenta=0x7f007f
cyan=0x007f7f
yellow=0x7f5100


def _ledspkl():
    t=.07; lookup=[red, orange, yellow, green, cyan, blue, magenta, white]             # .7x.07=.49s(colours)+.49(whites)=1s
    for k, v in enumerate(lookup): pycom.rgbled(v); time.sleep(t); pycom.rgbled(white); time.sleep(t)

def _setblueled():
    pycom.rgbled(blue)

def _setblueledblink(frequency):
    on = True
    while True:
        pycom.rgbled(blue)
        time.sleep(frequency)
        pycom.heartbeat(False)
        time.sleep(1.5)
