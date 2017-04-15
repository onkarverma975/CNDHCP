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


def check_sub(ip, net, mask):
    out = 0
    # print ip, net, mask
    for i in xrange(0,4):
        out = ip[i] ^ net[i]
        # print out
        out = out & mask[i]
        # print out
        if out !=0:
            return False
    return True

def add_IP(lac,net,mask):
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


    return check_sub(lac,net,mask)


def add_full_range(network, mask):
    network_copy = list(network)
    mask_copy = list(mask)

    for i in range(NUMBER_OF_OCTS):
        mask_copy[i] ^= 255
        network_copy[i] += mask_copy[i]
    return network_copy, mask_copy

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

    return convert_slash_mask_to_address(int(IP_V4_LENGTH - power)), int(IP_V4_LENGTH - power)



def check_overflow(network):
    for i in range(NUMBER_OF_OCTS - 1, -1, -1):
        if network[i] > BITS_IN_OCT:
            if i == 0:
                return "Operation exceeded IPv4 range"
            network[i] -= (BITS_IN_OCT + 1)
            network[i - 1] += 1
    return "good"



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


def add_one_to_network(network):
    network[NUMBER_OF_OCTS - 1] += 1

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

        host['mask'], host['mask_int'] = find_optimal_mask(host['number'])

        # print host['mask_int']

        host['NA'] = list(current_network)

        current_network = calculate_next_network(current_network, host['mask'])

        # calculate_next_network(current_network, host['mask'])
        if not is_network_valid(current_network, whole_network, mask):
            return hosts,True, 'Number of hosts exceeded capacity of given network'

            # raise Exception("Number of hosts exceeded capacity of given network")

        network_copy = list(host['NA'])

        mask_copy = list(host['mask'])

        broadcast_address = add_full_range(network_copy, mask_copy)[0]

        host['lac']=list(network_copy)

        add_one_to_network(network_copy)
        
        check_overflow(network_copy)
        
        host['first'] = list(network_copy)
        
        host['BA'] = list(broadcast_address)

        subtract_one_from_network(broadcast_address)

        host['last'] = list(broadcast_address)

    return hosts, False, 'good'


def correct_network(address, mask):
    for i in range(NUMBER_OF_OCTS):
        address[i] = address[i] & mask[i]

    return address


def check_network(address, mask):

    network_is_valid = is_network_valid(address, address, mask)
    if not network_is_valid:
        address = correct_network(address, mask)
    return address

class ServerIPs():
    def __init__(self):
        self.hosts=[]
        self.extras=[]
        self.lac=[0,0,0,0]
        self.network=[]
        self.mask=[]
        self.mask_int=0
        self.parse_input()
        self.network = correct_network(self.network, self.mask)
        self.hosts.sort(key=lambda x: x['number'], reverse=True)
        self.hosts, self.error_flag, self.error_string = calculate_available_addresses(self.hosts, self.network, self.mask)

        if self.error_flag:
            return

        self.BA = add_full_range(list(self.network), list(self.mask))[0]
        temp = list(self.network)
        add_IP(temp, self.network, self.mask)
        self.DNS = temp
        self.GATE = temp
        # self.lac = list(self.network)
        if len(self.hosts)-1>0:
            self.lac = list(self.hosts[len(self.hosts)-1]['BA'])
        else: 
            self.lac = list(self.network)
    def fetch_error(self):
        if self.error_flag:
            return self.error_string
        else:
            return ''
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
            ,'mask_int':0
            ,'NA':[]
            ,'BA':[]
            ,'first':[]
            ,'last':[]
            ,'lac':[]
            ,'count':0
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
        self.mask_int = mask
        self.mask = convert_slash_mask_to_address(mask)


    def getIP(self,mac):
        ret = {}
        for host in self.hosts:

            if host['mac']==mac:

                if not add_IP(host['lac'], host['NA'], host['mask']):

                    ret['type']='er'
                    ret['msg'] = 'No more IPs available in the subnet'
                    ret['code']=1

                    return ret, 'er'

                if host['count'] > host['number']:


                    ret['type']='er'
                    ret['code']=2
                    ret['msg'] = 'You have exceeded you limit, IP not assigned'

                    return ret,'er'

                ret['type']='ach'
                count=0
                for i in xrange(0,4):
                    count+=str(host['mask'][i]&255).count('1')
                ret['CIDR']= '.'.join(map(str, host['lac'])) + '/' + str(host['mask_int'])
                ret['NA'] = '.'.join(map(str, host['NA']))
                ret['LAB']= host['name']
                ret['BA'] = '.'.join(map(str, host['BA']))
                ret['DNS'] = '.'.join(map(str, host['first']))
                ret['GATE'] = '.'.join(map(str, host['first']))
                host['count']+=1


                return ret, 'got'

        return {}, 'nf'
        
    def newIP(self,mac):
        ret = {}
        if not add_IP(self.lac, self.network, self.mask):
            ret['code']=3
            ret['type']='er'
            ret['msg'] = 'No more IPs available for non Lab PCs'

            return ret,'er'

        ret['type']='acn'
        count=0
        for i in xrange(0,4):
            count+=str(self.mask[i]&255).count('1')
        ret['CIDR']= '.'.join(map(str, self.lac)) + '/' + str(self.mask_int)
        ret['NA'] = '.'.join(map(str, self.network))
        ret['BA'] = '.'.join(map(str, self.BA))
        self.extras.append((('.'.join(map(str, self.lac))),mac))
        ret['DNS'] =  '.'.join(map(str, self.DNS))
        ret['GATE'] =  '.'.join(map(str, self.GATE))
        return ret,'hello'
        

    def new_client(self,mac):
        
        ret,msg = self.getIP(mac)
        
        if msg == 'nf':
            ret, msg = self.newIP(mac)
        return ret