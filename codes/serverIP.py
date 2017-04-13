#This file is used to extract information from the subnets file and then pass it on back to the server
import getopt
import os
import sys

DOT_DELIMITER = '.'
COMMA_DELIMITER = ','
INFO_TAG = "[*]"
IP_V4_LENGTH = 32
NUMBER_OF_OCTS = IP_V4_LENGTH // 8
BITS_IN_OCT = 255

def get_info(data):
    data = data.split('\n')[0]

    temp = data.split('/')
    ip = temp[0]
    mask = int(temp[1])
    ip = ip.split('.')
    ip = list(map(int, ip))
    return ip, mask
def add_IP(lac):
    lac[3]+=1
    if lac[3]>255:
        lac[3]=0
        lac[2]+=1
    if lac[2]>255:
        lac[2]=0
        lac[1]+=1
    if lac[1]>255:
        lac[1]=0
        lac[0]+=1
    for i in lac:
        if i>255:
            return False
    return True


def convert_slash_mask_to_address(mask):
    address_mask = []

    for i in range(NUMBER_OF_OCTS):
        if mask >= 8:
            address_mask.append(255)
            mask -= 8
        elif mask > 0:
            address_mask.append(int("1" * mask + "0" * (8 - mask), 2))
            mask = 0
        else:
            address_mask.append(int(0))

    return address_mask


def find_optimal_mask(host_demand):
    host_capacity = 0
    power = 1

    while host_capacity < host_demand:
        power += 1
        host_capacity = (2 ** power) - 2

    return convert_slash_mask_to_address(int(IP_V4_LENGTH - power))


def add_full_range(network, mask):
    network_copy = list(network)
    mask_copy = list(mask)

    for i in range(NUMBER_OF_OCTS):
        mask_copy[i] ^= 255
        network_copy[i] += mask_copy[i]
    return network_copy, mask_copy


def check_overflow(network):
    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network[i] > BITS_IN_OCT:
            if i == 0:
                raise Exception("Operation exceeded IPv4 range")
            network[i] -= (BITS_IN_OCT + 1)
            network[i - 1] += 1


def add_one_to_network(network):
    network[NUMBER_OF_OCTS - 1] += 1


def subtract_one_from_network(network):
    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network[i] != 0:
            network[i] -= 1
            break


def calculate_next_network(current_network, current_mask):
    network, mask = add_full_range(current_network, current_mask)
    add_one_to_network(network)
    check_overflow(network)

    return network


def is_network_valid(network_to_validate, whole_network, mask):
    for i in range(NUMBER_OF_OCTS):
        if network_to_validate[i] & mask[i] != whole_network[i]:
            return False

    return True




def calculate_available_addresses(hosts, network, mask):
    
    whole_network = list(network)
    
    result = []

    current_network = list(network)


    for host in hosts:

        host['mask'] = find_optimal_mask(host['number'])

        print host['mask']

        host['NA'] = list(current_network)

        current_network = calculate_next_network(current_network, host['mask'])

        # calculate_next_network(current_network, host['mask'])
 
        if not is_network_valid(current_network, whole_network, mask):
            raise Exception("Number of hosts exceeded capacity of given network")

        network_copy = list(host['NA'])

        mask_copy = list(host['mask'])

        broadcast_address = add_full_range(network_copy, mask_copy)[0]

        add_one_to_network(network_copy)
        
        check_overflow(network_copy)
        
        host['first'] = list(network_copy)
        
        host['BA'] = list(broadcast_address)

        subtract_one_from_network(broadcast_address)

        host['last'] = list(broadcast_address)

    return hosts


def correct_network(address, mask):
    for i in range(NUMBER_OF_OCTS):
        address[i] = address[i] & mask[i]

    return address


def check_network(address, mask):

    network_is_valid = is_network_valid(address, address, mask)
    if not network_is_valid:
        print("[!] Mask does not cover the whole network [!]")
        print("[!] Attempting to correct the mask by ANDing Network and MASK [!]")
        print("\n")
        address = correct_network(address, mask)

    return address


class ServerIPs():
    def __init__(self):
        self.hosts=[]
        self.extras=[]
        self.lac=[0,0,0,0]
        self.network=[]
        self.mask=[]
        self.parse_input()
        self.network = correct_network(self.network, self.mask)
        self.hosts.sort(key=lambda x: x['number'], reverse=True)
        self.hosts = calculate_available_addresses(self.hosts,self.network, self.mask)
        self.lac = self.hosts[len(self.hosts)-1]['BA']
    def parse_input(self):
        f= open("subnets.conf","r")
        contents = f.readline()
        network, mask = get_info(contents)

        n_hosts = int(f.readline())
        for i in xrange(n_hosts):
            line = f.readline()
            line = line.split(':')
            temp = {
            'name':line[0]
            ,'number':int(line[1])
            ,'mac':''
            ,'mask':[]
            ,'NA':[]
            ,'BA':[]
            ,'first':[]
            ,'last':[]
            ,'lac':[]
            }
            self.hosts.append(temp)
            self.lac = temp['BA']


        for i in xrange(n_hosts):
            line = f.readline()
            line = line.split(' ')
            line[1] = line[1].split('\n')[0]
            for host in self.hosts:
                if host['name']==line[1]:
                    host['mac']=line[0]
        f.close()
        self.network = network
        self.mask = convert_slash_mask_to_address(mask)

    def getIP(self,mac):
        for host in self.hosts:
            if host['mac']==mac:
                if not add_IP(host['lac']):
                    return 'overflow', None
                if host['lac'] == host['last']:
                    return 'overflow', None
                return '.'.join(map(str, host['lac'])), host
        return 'not_found', None
        
    def newIP(self,mac):
        if not add_IP(self.lac):
            #run out of ips
            return 'overflow'
            pass
            return
        self.extras.append((('.'.join(map(str, self.lac))),mac))
        return '.'.join(map(str, self.lac))

    def new_client(self,mac):
        
        new_ip = self.getIP(mac)
        
        ret = {}

        if new_ip == 'not_found':
            ret_msg = self.newIP(mac)
            if ret_msg == 'overflow':
                ret_type='er'
                ret_msg = 'No more IPs available in Network'
            else:
                ret_type='acm'

        else if new_ip == 'overflow'
            ret_type='er'
            ret_msg = 'No more IPs available in Sub-Network'
        else:
            ret_type=''
        ret['type'] = ret_type
        ret['msg'] = ret_msg

        return ret