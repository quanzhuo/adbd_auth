#!/usr/bin/env python3

import socketserver
import re
import datetime
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import FileModifiedEvent

allowed_devices = []
denied_devices = []

class ProductIdChangeHandler(FileSystemEventHandler):

    "This mothod is executed if allow.txt/deny.txt is changed"
    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            if event.src_path.endswith("allow.txt"):
                with open("allow.txt") as f:
                    global allowed_devices
                    del allowed_devices[:]
                    for line in f:
                        id = line.strip('\n')
                        allowed_devices.append(id)
                        print(datetime.datetime.now(), "Add", id, "to allow.txt")
            elif event.src_path.endswith("deny.txt"):
                with open("deny.txt") as f:
                    global denied_devices
                    del denied_devices[:]
                    for line in f:
                        id = line.strip('\n')
                        denied_devices.append(id)
                        print(datetime.datetime.now(), "Add", id, "to deny.txt")

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

        # if productid is in deny.txt, drop it
        if productid in denied_devices:
            self.request.send(b'1')
            print(datetime.datetime.now(), "Deny", productid, "from", IP,
                  "It's in deny.txt")
        elif self.is_in_zzdc(IP):
            self.request.send(b'0')
            print(datetime.datetime.now(), "Allow", productid, "from", IP)
        else:
            if productid in allowed_devices:
                self.request.send(b'0')
                print(datetime.datetime.now(), "Allow", productid, 
                      "It's in allow.txt, IP:", IP)
            else:
                self.request.send(b'1')
                print(datetime.datetime.now(), "Deny", productid, 
                      "It's not in allow.txt, IP:", IP)

        self.request.close()

    def is_in_zzdc(self, ip):
        "wether the request is from zzdc"
    
        if re.search(r"10.206.2[45].[0-9]{1,3}", ip):
            return True
        else:
            return False

if __name__ == '__main__':
    with open("allow.txt") as f:
        for productid in f:
            allowed_devices.append(productid.strip('\n'))

    with open("deny.txt") as f:
        for productid in f:
            denied_devices.append(productid.strip('\n'))

    event_handler = ProductIdChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    addr_port = ('0.0.0.0', 6666)
    with socketserver.ThreadingTCPServer(addr_port, ADBAuthHandler) as server:
        server.serve_forever()
