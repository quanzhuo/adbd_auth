#!/usr/bin/env python3

import socketserver
import re
import datetime

allow = 0
deny = 0

def is_in_zzdc(ip):
	"wether the request is from zzdc"
	
	if re.search(r"10.206.2[45].[0-9]{1,3}", ip):
		print(datetime.datetime.now(), ip, "is in zzdc")
		return True
	else:
		print(datetime.datetime.now(), ip, "is not in zzdc, allow anyway !")
		return True

class ADBAuthHandler(socketserver.StreamRequestHandler):
	"""
	The request handler class for our server

	It is instantiated once per connection to the server, and must 
	override the handle() method to implement communication to the
	client
	"""
	def handle(self):
		global allow, deny

		IP, _ = self.client_address

		if is_in_zzdc(IP):
			allow += 1
			self.request.send(b'0')
		else:
			deny += 1
			self.request.send(b'1')

		print("allow:", allow, "deny:", deny)

		self.request.close()

if __name__ == '__main__':
	addr_port = ('0.0.0.0', 6666)
	with socketserver.ThreadingTCPServer(addr_port, ADBAuthHandler) as server:
		server.serve_forever()
