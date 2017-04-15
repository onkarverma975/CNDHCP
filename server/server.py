import argparse
import socket
import struct
import random
import uuid
import json
from serverIP import ServerIPs
import signal
import sys
def signal_handler(signal, frame):
        print('Closing Server')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

MAX_BYTES=65535
def getIP(mac):
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def fun_server():
    server = ServerIPs()
    if server.fetch_error() is not '':
        print server.fetch_error()
        print "Server closing due to error"
        return
    dsocket=socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
    dsocket.setsockopt(socket.SOL_SOCKET , socket.SO_BROADCAST, 1)
    dsocket.bind(('',6700))
    # print('Listening at {}'.format(dsocket.getsockname()))
    while True:
        data , address = dsocket.recvfrom(MAX_BYTES)
        

        #Find Discover Package
        obj = json.loads(data)

        if obj['type']=='offer':
            print 'received a request from MAC address', obj['mac']
                        
            ret = server.new_client(obj['mac'])
            
            ret_str = json.dumps(ret)
            dsocket.sendto(ret_str,('<broadcast>',6800))
            # print 'sent back the reposone', ret


fun_server()