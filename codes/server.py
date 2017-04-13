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
                        
            ret = server.new_client(obj['mac'])
            
            ret_str = json.dumps(ret)
            dsocket.sendto(ret_str,('<broadcast>',6800))
            print 'sent back the reposone' ret



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