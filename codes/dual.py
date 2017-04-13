#!usr/bin/env python3
import argparse
import socket
import struct
import random
import uuid
from client import *
from server import *

if  __name__ == '__main__':
    choice={'client':client , 'server':server}
    parser = argparse.ArgumentParser(description='DHCP Implement')
    parser.add_argument('role', choices = choice , help='which role to play')
    args=parser.parse_args()
    function=choice[args.role]
    function()