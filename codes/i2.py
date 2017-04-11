import getopt
import os
import sys

from prints import *

DOT_DELIMITER = '.'
COMMA_DELIMITER = ','
INFO_TAG = "[*]"
IP_V4_LENGTH = 32
NUMBER_OF_OCTS = IP_V4_LENGTH // 8
BITS_IN_OCT = 255

verbose = False


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def convert_slash_mask_to_address(mask):
    address_mask = []

    mask = int(mask[1:])

    for i in range(NUMBER_OF_OCTS):
        if mask >= 8:
            address_mask.append(255)
            mask -= 8
        elif mask > 0:
            address_mask.append(int("1" * mask + "0" * (8 - mask), 2))
            mask = 0
        else:
            address_mask.append(0)

    return address_mask


def find_optimal_mask(host_demand):
    host_capacity = 0
    power = 1

    while host_capacity < host_demand:
        power += 1
        host_capacity = (2 ** power) - 2

    return convert_slash_mask_to_address("/" + str(IP_V4_LENGTH - power))


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


def calculate_networks(network, mask, hosts):
    whole_network = list(network)
    result = []

    current_network = list(network)
    for host_number in hosts:
        current_mask = find_optimal_mask(host_number)
        result.append((current_network, current_mask))

        current_network = calculate_next_network(current_network, current_mask)
        if not is_network_valid(current_network, whole_network, mask):
            raise Exception("Number of hosts exceeded capacity of given network")

    return result


def calculate_available_addresses(networks):
    networks_count = len(networks)
    available_addresses = []

    for i in range(networks_count):
        network_copy = list(networks[i][0])
        mask_copy = list(networks[i][1])

        broadcast_address = add_full_range(network_copy, mask_copy)[0]
        add_one_to_network(network_copy)
        check_overflow(network_copy)
        first_address = network_copy
        last_address = list(broadcast_address)
        subtract_one_from_network(last_address)

        available_addresses.append((first_address, last_address, broadcast_address))

    return available_addresses


def convert_ip_to_str(address):
    return DOT_DELIMITER.join(str(x) for x in address)


def correct_network(address, mask):
    for i in range(NUMBER_OF_OCTS):
        address[i] = address[i] & mask[i]

    return address


def check_network(address, mask):
    if verbose:
        print_info("Checking network")

    network_is_valid = is_network_valid(address, address, mask)
    if not network_is_valid:
        print("[!] Mask does not cover the whole network [!]")
        print("[!] Attempting to correct the mask by ANDing Network and MASK [!]")
        print("\n")
        address = correct_network(address, mask)

    if verbose and network_is_valid:
        print_info("Network is valid")
        print("\n")
    return address


def convert_oct_to_bin(oct):
    oct = bin(oct)[2:]
    l = len(oct)
    if l < 8:
        oct = "0" * (8 - l) + oct
    return oct

def main():
    cls()
    network, mask, hosts = parse_input()

    network = convert_input_to_array(network, DOT_DELIMITER)
    hosts = convert_input_to_array(hosts, COMMA_DELIMITER)
    
    network = check_network(network, mask)

    hosts.sort(reverse=True)

    if verbose:
        print_info("Calculating networks")
        print("")
    calculated_networks = calculate_networks(network, mask, hosts)
    available_addresses = calculate_available_addresses(calculated_networks)
    print_result(calculated_networks, hosts, available_addresses)


main()