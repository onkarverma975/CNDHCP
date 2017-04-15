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
    dsocket.settimeout(2)
    data, address = dsocket.recvfrom(MAX_BYTES)
    if data:
        serverIP=address
        res_obj = json.loads(data)
        print_response(res_obj)
       


def print_response(obj): 
	if obj['type']=='er':
		print 'Error: ', obj['msg'], obj['code']
	elif obj['type']=='ach':
		print 'Lab: ', obj['LAB']
		print obj['CIDR']
		print obj['NA']
		print obj['BA']
		print obj['GATE']
		print obj['DNS']

	elif obj['type']=='acn':
		print obj['CIDR']
		print obj['NA']
		print obj['BA']
		print obj['GATE']
		print obj['DNS']
def main():
	inp = sys.argv
	if len(sys.argv) == 1:
		client(str(getHwAddr('enp2s0')).upper())
		pass
	elif len(sys.argv)==3 and inp[1]=='-m':
		client(str(inp[2]).upper())
		pass

main()
