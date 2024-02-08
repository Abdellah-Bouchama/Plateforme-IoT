# Author: Igor Ferreira
# License: MIT
# Version: 2.1.0
# Description: WiFi Manager for ESP8266 and ESP32 using MicroPython.

import machine
import network
import socket
import re
import time
import lib.logging as logger
import lib.config as config


WMASSAGE_PERIOD = const(5)

class WifiManager:

    def __init__(self, ssid = config.WIFI_SSID, password = config.WIFI_PW, reboot = True):
        self.wlan_sta = network.WLAN(mode=network.WLAN.STA)
        self.wlan_ap = network.WLAN(network.WLAN.AP)
        
        
        # Avoids simple mistakes with wifi ssid and password lengths, but doesn't check for forbidden or unsupported characters.
        if len(ssid) > 32:
            raise Exception('The SSID cannot be longer than 32 characters.')
            print("11")
        else:
            self.ap_ssid = ssid
            print("1")
        if len(password) < 8:
            raise Exception('The password cannot be less than 8 characters long.')
            print("11")
        else:
            self.ap_password = password
            print("1")
            
        # Set the access point authentication mode to WPA2-PSK.
        self.ap_authmode = 3
        print("1")
        
        # The file were the credentials will be stored.
        # There is no encryption, it's just a plain text archive. Be aware of this security problem!
        self.ssid = ''
        self.wifi_credentials = 'wifi.dat'
        
        # Prevents the device from automatically trying to connect to the last saved network without first going through the steps defined in the code.
        self.wlan_sta.disconnect()
        
        # Change to True if you want the device to reboot after configuration.
        # Useful if you're having problems with web server applications after WiFi configuration.
        self.reboot = reboot
        
        
        self.logger = logger


    #Connect to one of already known connections
    def connect(self):
        if self.wlan_sta.isconnected():
            return
        profiles = self.read_credentials()
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            if ssid in profiles:
                password = profiles[ssid]
                if self.wifi_connect(ssid, password):
                    self.ssid = ssid
                    return
        print('Could not connect to any WiFi network. Starting the configuration portal...')
        self.web_server()
        
    
    def disconnect(self):
        if self.is_connected():
            self.wlan_sta.disconnect()


    def is_connected(self):
        return self.wlan_sta.isconnected()


    def get_address(self):
        return self.wlan_sta.ifconfig()
    
    def check_status(self):
        if self.wlan_sta.isconnected():
            self.logger.info("Device connected to {}".format(self.ssid))
        else:
            self.logger.warning("Not Connected to wifi")



    def write_credentials(self, profiles):
        lines = []
        for ssid, password in profiles.items():
            lines.append('{0};{1}\n'.format(ssid, password))
        with open(self.wifi_credentials, 'w') as file:
            file.write(''.join(lines))


    def read_credentials(self):
        lines = []
        try:
            with open(self.wifi_credentials) as file:
                lines = file.readlines()
        except Exception as error:
            pass
        profiles = {}
        for line in lines:
            ssid, password = line.strip().split(';')
            profiles[ssid] = password
        return profiles


    def wifi_connect(self, ssid, password, timeout):
        print('Trying to connect to:', ssid)
        self.wlan_sta.connect(ssid, auth=(network.WLAN.WPA2, password))
        #for _ in range(100):
        waiting_deadline = time.time() + timeout ## Wait <timeout> seconds for connexion binding
        while not self.wlan_sta.isconnected():
            if time.time()> waiting_deadline :
                self.logger.warning("Not connected to network, binding timed out")
                break
            time.sleep_ms(500)
            print("Waiting for connection to wifi")
            if self.wlan_sta.isconnected():
                print('\nConnected to wifi {} Network information:{}'.format(ssid, self.get_address()))
                self.ssid = ssid
                return True
            else:
                print('.', end='')
                time.sleep_ms(100)
        print('\nConnection failed!')
        self.wlan_sta.disconnect()
        return False

    def ap_broadcast(self):

        
        self.wlan_ap.init(mode =network.WLAN.AP, ssid =self.ap_ssid, auth = (network.WLAN.WPA2, self.ap_password))
        #Waiting for clients to be connected on the AP
        print("Actvating {} access point on the fipy please wait".format(self.ap_ssid))
        last_print_time = time.time()
        while not self.wlan_ap.isconnected():
            current_time = time.time()
            if current_time - last_print_time >= WMASSAGE_PERIOD:
                print("Still waiting... Please wait for client...")
                last_print_time = current_time
            
        self.logger.info("Client connected")
        print("Braodcasting AP signal on {}".format(self.ap_ssid))
        print(self.wlan_ap.ifconfig())
    
    def web_server(self):
        #self.wlan_ap.active(True)
        self.wlan_ap.init(mode =network.WLAN.AP, ssid =self.ap_ssid, auth = (network.WLAN.WPA2, self.ap_password))
        server_socket = socket.socket()
        server_socket.close()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', 80))
        server_socket.listen(1)
        print('Connect to', self.ap_ssid, 'with the password', self.ap_password, 'and access the captive portal at', self.wlan_ap.ifconfig()[0])
        while True:
            if self.wlan_sta.isconnected():
                self.wlan_ap.active(False)
                if self.reboot:
                    print('The device will reboot in 5 seconds.')
                    time.sleep(5)
                    machine.reset()
            self.client, addr = server_socket.accept()
            try:
                self.client.settimeout(5.0)
                self.request = b''
                try:
                    while True:
                        if '\r\n\r\n' in self.request:
                            # Fix for Safari browser
                            self.request += self.client.recv(512)
                            break
                        self.request += self.client.recv(128)
                except Exception as error:
                    # It's normal to receive timeout errors in this stage, we can safely ignore them.
                    pass
                if self.request:
                    url = re.search('(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP', self.request).group(1).decode('utf-8').rstrip('/')
                    if url == '':
                        self.handle_root()
                    elif url == 'configure':
                        self.handle_configure()
                    else:
                        self.handle_not_found()
            except Exception as error:
                return
            finally:
                self.client.close()


    def send_header(self, status_code = 200):
        self.client.send("""HTTP/1.1 {0} OK\r\n""".format(status_code))
        self.client.send("""Content-Type: text/html\r\n""")
        self.client.send("""Connection: close\r\n""")


    def send_response(self, payload, status_code = 200):
        self.send_header(status_code)
        self.client.sendall("""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    {0}
                </body>
            </html>
        """.format(payload))
        self.client.close()


    def handle_root(self):
        self.send_header()
        self.client.sendall("""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <title>WiFi Manager</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="icon" href="data:,">
                </head>
                <body>
                    <h1>WiFi Manager</h1>
                    <form action="/configure" method="post" accept-charset="utf-8">
        """.format(self.ap_ssid))
        for ssid, *_ in self.wlan_sta.scan():
            ssid = ssid.decode("utf-8")
            self.client.sendall("""
                        <p><input type="radio" name="ssid" value="{0}" id="{0}"><label for="{0}">&nbsp;{0}</label></p>
            """.format(ssid))
        self.client.sendall("""
                        <p><label for="password">Password:&nbsp;</label><input type="password" id="password" name="password"></p>
                        <p><input type="submit" value="Connect"></p>
                    </form>
                </body>
            </html>
        """)
        self.client.close()


    def handle_configure(self):
        match = re.search('ssid=([^&]*)&password=(.*)', self.url_decode(self.request))
        if match:
            ssid = match.group(1).decode('utf-8')
            password = match.group(2).decode('utf-8')
            if len(ssid) == 0:
                self.send_response("""
                    <p>SSID must be providaded!</p>
                    <p>Go back and try again!</p>
                """, 400)
            elif self.wifi_connect(ssid, password):
                self.send_response("""
                    <p>Successfully connected to</p>
                    <h1>{0}</h1>
                    <p>IP address: {1}</p>
                """.format(ssid, self.wlan_sta.ifconfig()[0]))
                profiles = self.read_credentials()
                profiles[ssid] = password
                self.write_credentials(profiles)
                time.sleep(5)
            else:
                self.send_response("""
                    <p>Could not connect to</p>
                    <h1>{0}</h1>
                    <p>Go back and try again!</p>
                """.format(ssid))
                time.sleep(5)
        else:
            self.send_response("""
                <p>Parameters not found!</p>
            """, 400)
            time.sleep(5)


    def handle_not_found(self):
        self.send_response("""
            <p>Page not found!</p>
        """, 404)


    def url_decode(self, url_string):

        # Source: https://forum.micropython.org/viewtopic.php?t=3076
        # unquote('abc%20def') -> b'abc def'
        # Note: strings are encoded as UTF-8. This is only an issue if it contains
        # unescaped non-ASCII characters, which URIs should not.

        if not url_string:
            return b''

        if isinstance(url_string, str):
            url_string = url_string.encode('utf-8')

        bits = url_string.split(b'%')

        if len(bits) == 1:
            return url_string

        res = [bits[0]]
        appnd = res.append
        hextobyte_cache = {}

        for item in bits[1:]:
            try:
                code = item[:2]
                char = hextobyte_cache.get(code)
                if char is None:
                    char = hextobyte_cache[code] = bytes([int(code, 16)])
                appnd(char)
                appnd(item[2:])
            except Exception as error:
                appnd(b'%')
                appnd(item)

        return b''.join(res)
    
    def ipV4_config(self, ip, subnet, gateway, dns):

        self.wlan_sta.ifconfig(config=(ip, subnet, gateway, dns))