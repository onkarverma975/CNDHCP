import argparse
import socket
import struct
import random
import json
import sys

MAX_BYTES=65535

import fcntl, socket, struct

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])



def IPInByte(ip):
    ips=ip.split('.')
    byte=b''
    for i in range(4):
        byte+=struct.pack('!B',int(ips[i]))
    return byte


def assignIP(ip):
    print 'set the ip as',ip
    return ip

class DHCPDiscover:
    def __init__(self, mac):
        self.mac    = mac
    def build(self):
        print self.mac
        obj = {'mac':self.mac,'type':'offer'}
        # obj['mac']=self.mac
        # obj['type']='request'
        return json.dumps(obj)        


def client(mac):
    dsocket=socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
    dsocket.setsockopt(socket.SOL_SOCKET , socket.SO_BROADCAST, 1)

    dsocket.bind(('', 6800 ))

    discoverPackage=DHCPDiscover(mac)
    Discoverdata = discoverPackage.build()
    dsocket.sendto( Discoverdata , ('<broadcast>', 6700))
    print('DHCP Discover has sent. Wating for reply...\n')
    res_str=''
    serverIP=[]
    while True:
        data, address = dsocket.recvfrom(MAX_BYTES)
        if data:
            serverIP=address
            res_obj = json.loads(data)
            assignIP(res_obj['clientIP'])


    # while True:
    #     data, address = dsocket.recvfrom(MAX_BYTES)
    #     serverIP=address[0]
    #     if transID==data[4:8]:
    #         requestIP=data[16:20]
    #         data=b''
    #         data=Discoverdata[:240]
    #         data+=b'\x35\x01\x03'                  # Option53: length1 , type 3 DHCP Request 
    #         data+=b'\x32\x04'+requestIP          # Option 50: length 4 , request IP
    #         data+=b'\x36\x04'+IPInByte(address[0]) # Option 54: length 4 , identifier
    #         data+=b'\xff'
    #         dsocket.sendto(data, ('<broadcast>', 67))
    #         break

    # while True:
    #     data, address = dsocket.recvfrom(MAX_BYTES)
    #     if transID==data[4:8] and data.find(b'\x35\x01\x05') and serverIP==address[0]:
    #         RequestIP= '.'.join(map(lambda x: str(x),data[16:20]))
    #         print("Request IP: {}".format(RequestIP))
    #         dsocket.close()
    #         break
            

def main():
	inp = sys.argv
	print 
	if len(sys.argv) == 1:
		client(str(getHwAddr('enp2s0')).upper())
		pass
	elif len(sys.argv)==3 and inp[1]=='-m':
		client(str(inp[2]).upper())
		pass

main()
