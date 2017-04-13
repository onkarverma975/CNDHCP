import argparse
import socket
import struct
import random
import uuid
import json
MAX_BYTES=65535

def getMacInByte():
    mac=str(hex(uuid.getnode()))
    mac = mac[2:]
    while len(mac) < 12:
        mac='0'+mac
    macb=b''
    for i in range( 0 , 12 , 2):
        m=int(mac[i:i+2],16)
        macb+=struct.pack('!B',m)
    # return macb
    return '80:0D:78:81:14:D1'


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
    def __init__(self):
        self.mac    = getMacInByte()        
    def build(self):
        print self.mac
        obj = {'mac':self.mac,'type':'offer'}
        # obj['mac']=self.mac
        # obj['type']='request'
        return json.dumps(obj)        


def client():
    dsocket=socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
    dsocket.setsockopt(socket.SOL_SOCKET , socket.SO_BROADCAST, 1)

    dsocket.bind(('', 6800 ))

    discoverPackage=DHCPDiscover()
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
            
