import getopt
import os
import sys

from prints import *
from file_processing import parse_input


DOT_DELIMITER = '.'
COMMA_DELIMITER = ','
INFO_TAG = "[*]"
IP_V4_LENGTH = 32
NUMBER_OF_OCTS = IP_V4_LENGTH // 8
BITS_IN_OCT = 255

verbose = False



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



def main():
    cls()
    network, mask, hosts = parse_input()

    mask = convert_slash_mask_to_address(mask)

    network = correct_network(network, mask)

    hosts.sort(key=lambda x: x['number'], reverse=True)

    hosts = calculate_available_addresses(hosts,network, mask)
    for host in hosts:
        print host
    # print_result(calculated_networks, hosts, available_addresses)


main()