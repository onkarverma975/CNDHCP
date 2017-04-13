import argparse
import socket
import struct
import random
import uuid
import json
from serverIP import ServerIPs

MAX_BYTES=65535
def getIP(mac):
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def fun_server():
    server = ServerIPs()
    dsocket=socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
    dsocket.setsockopt(socket.SOL_SOCKET , socket.SO_BROADCAST, 1)
    dsocket.bind(('',6700))
    print('Listening at {}'.format(dsocket.getsockname()))
    while True:
        data , address = dsocket.recvfrom(MAX_BYTES)
        print 'received a request',data

        #Find Discover Package
        obj = json.loads(data)

        if obj['type']=='offer':
            
            ret = {}
            
            ret['clientIP']=server.newIP(obj['mac'])
            
            ret_str = json.dumps(ret)
            dsocket.sendto(ret_str,('<broadcast>',6800))
            print 'sent back the reposone'

        # if(data[240:].find(b'\x35\x01\x01')!=-1):
        #     offerAddr=b'\xc0\xa8'
        #     for i in range(2):
        #         t=random.randint(0,255)
        #         offerAddr+=struct.pack('!B',t)
        #     payload=b'\x02'+data[1:16]
        #     payload+=offerAddr
        #     payload+=data[20:240]
        #     payload+=b'\x35\x01\x02'
        #     payload+=b'\xff'
        #     dsocket.sendto(payload,('<broadcast>',68))

        # #Find Request Package
        # if(data[240:].find(b'\x35\x01\x03')!=-1):
        #     selfIP=IPInByte(socket.gethostbyname(socket.gethostname()))
        #     pat=b'\x36\x04'+selfIP              # request identify
        #     if(data[240:].find(pat)!=-1):
        #         if(data[240:].find(b'\x32\x04')!=-1):
        #             find=data[240:].find(b'\x32\x04')
        #             requestIP=data[240:][find+2:find+6]
        #             payload=b'\x02'+data[1:16]
        #             payload+=requestIP
        #             payload+=data[20:240]
        #             payload+=b'\x35\x01\x05'
        #             payload+=b'\xff'
        #             dsocket.sendto(payload,('<broadcast>',68))
        #     else:
        #         continue

