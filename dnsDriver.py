#!/usr/bin/env python3

import argparse
from dnsSetup.dns import *
import socket

#TODO REMOVE THESE DEFAULTS LATER
DEFAULT_PORT = 40015
DEFAULT_NAME = "cs5700cdn.example.com"

def main():

    parser = argparse.ArgumentParser(description='Parser for dnsserver args')
    parser.add_argument('-p','--port', metavar='',type=int,help='Port that the dns server will bind to')
    parser.add_argument('-n', '--name',metavar='',help='domain name for your "customer", i.e. the only name your DNS server should resolve to replica IPs')
    parser.add_argument('-d', '--default', metavar='',
                        help='exclusive arg, if called uses default port and name values')
    args = parser.parse_args()

    #TODO REMOVE FOR FINA
    args.port = DEFAULT_PORT
    args.name = DEFAULT_NAME

    if args.default != None:
        args.port = DEFAULT_PORT
        args.name = DEFAULT_NAME
    else:
        if args.port == None:
            print("ERROR: Missing port (-p) argument!")
            print("DNS server cannot be run ")
            print("EXITING PROGRAM")
            exit(0)
        elif args.name == None:
            print("ERROR: Missing name (-n) argument!")
            print("DNS server cannot be run ")
            print("EXITING PROGRAM")
            exit(0)


    dns_instance = DNSServer(dns_port=args.port, customer_name=args.name,
                                 display=True, display_geo_load=True)
    dns_instance.listen_for_clients()
    dns_instance.close_server()

if __name__ == "__main__":
    main()