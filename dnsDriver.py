#!/usr/bin/env python3
import argparse
from dns import *


DEFAULT_PORT = 40015
DEFAULT_NAME = "cs5700cdn.example.com"

def main():

    parser = argparse.ArgumentParser(description="Parser for dnsserver args")
    parser.add_argument(
        "-p",
        "--port",
        metavar="",
        type=int,
        help="Port that the dns server will bind to",
    )
    parser.add_argument(
        "-n",
        "--name",
        metavar="",
        help='domain name for your "customer", i.e. the only name your DNS server should resolve to replica IPs',
    )

    #-----------------------------------------------------------------------------------------------------
    #optional args
    parser.add_argument(
        "-d",
        "--default",
        metavar="",
        help="optional, exclusive arg, if not None default port and name values and displays print statements",
    )
    parser.add_argument(
        "-s",
        "--display",
        metavar="",
        help="optional arg, if not None displays print statements",
    )
    args = parser.parse_args()

    display_prints = False

    if args.display != None:
        display_prints = True

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

    dns_instance = DNSServer(
        dns_port=args.port,
        customer_name=args.name,
        display=display_prints,
        display_geo_load=display_prints
    )
    dns_instance.listen_for_clients(display_prints)
    dns_instance.close_server()


if __name__ == "__main__":
    main()
