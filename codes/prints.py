import getopt
import os
import sys

DOT_DELIMITER = '.'
COMMA_DELIMITER = ','
INFO_TAG = "[*]"
IP_V4_LENGTH = 32
NUMBER_OF_OCTS = IP_V4_LENGTH // 8
BITS_IN_OCT = 255

verbose = False



def print_help():
    print("VLSM subnetting tool for IPv4")
    print('')
    print("usage:\nvlsm.py -n network_address -m mask -h hosts\n")
    print("options:")
    print("-v\t Have vlsm.py give more verbose output.")
    print("\n")
    print("Examples:")
    print("vlsm.py -n 192.168.1.0 -m 255.255.255.0 -h 100,50,25,5")
    print("vlsm.py -n 192.168.1.0 -m /24 -h 50,25,100,5")

    sys.exit(0)


def print_error(error):
    print(error)
    print("If you need help type: vlsm.py --help")
    sys.exit(0)


def print_info(message):
    print("{0} {1} {2}".format(INFO_TAG, message, INFO_TAG))


def print_result(networks, demanded_hosts, available_addresses):
    networks_count = len(networks)
    for i in range(networks_count):
        network = networks[i][0]
        mask = networks[i][1]
        broadcast = available_addresses[i][2]
        first_address = available_addresses[i][0]
        last_address = available_addresses[i][1]

        print("Network #{0} (demanded hosts:{1}):".format(i + 1, demanded_hosts[i]))
        print("Network address: {0}".format(convert_ip_to_str(network)))
        if verbose:
            print_ip_binary(network)
            print("")
        print("Network mask: {0}".format(convert_ip_to_str(mask)))
        if verbose:
            print_ip_binary(mask)
            print("")
        print("Broadcast address: {0}".format(convert_ip_to_str(broadcast)))
        if verbose:
            print_ip_binary(broadcast)
            print("")
        print("Available addresses for hosts: {0} - {1}".format(convert_ip_to_str(first_address),
                                                                convert_ip_to_str(last_address)))
        if verbose:
            print("First address:")
            print_ip_binary(first_address)
            print("Last address:")
            print_ip_binary(last_address)
            print("")
        print("")



def print_ip_decimal(ip):
    s = convert_ip_to_str(ip)
    print(s)


def print_ip_binary(ip):
    s = DOT_DELIMITER.join(convert_oct_to_bin(i) for i in ip)
    print(s)


def print_ip(ip, is_decimal_form, is_binary_form):
    if is_decimal_form:
        print_ip_decimal(ip)
    if is_binary_form:
        print_ip_binary(ip)


def print_arguments(network, mask):
    print_info("Given network:")
    print_ip(network, True, True)
    print("")

    print_info("Given mask:")
    print_ip(mask, True, True)
    print("\n")

