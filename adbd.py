#!/usr/bin/env python3

import socketserver
import re
import datetime

productids = []

class ADBAuthHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for our server

    It is instantiated once per connection to the server, and must 
    override the handle() method to implement communication to the
    client
    """

    def handle(self):
        # self.request is the Tcp socket connected to the client
        productid = self.request.recv(16).strip().decode()
        IP, _ = self.client_address

        if self.is_in_zzdc(IP):
            self.request.send(b'0');
            print("Allow", productid, "from", IP)
        else:
            if self.is_productid_allowed(productid):
                self.request.send(b'0');
                print("Allow", productid, "It's in productid list, IP:", IP)
            else:
                self.request.send(b'1');
                print("Deny", productid, "It's not in productid list, IP:", IP)

        self.request.close()

    def is_productid_allowed(self, productid):
        global productids
        if productid in productids:
            return True
        else:
            return False
    
    def is_in_zzdc(self, ip):
        "wether the request is from zzdc"
    
        if re.search(r"10.206.2[45].[0-9]{1,3}", ip):
            return True
        else:
            return False

if __name__ == '__main__':
    with open("productid.txt") as f:
        for productid in f:
            productids.append(productid.strip('\n'))

    addr_port = ('0.0.0.0', 6666)
    with socketserver.ThreadingTCPServer(addr_port, ADBAuthHandler) as server:
        server.serve_forever()
