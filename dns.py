#!/usr/bin/env python3
import os
import socket
from dnslib import DNSRecord, DNSHeader, DNSQuestion, RR, A, RCODE
from typing import Tuple

from geo_db import geo_db
import requests
from math import radians, cos, sin, asin, sqrt
import random
from urllib.parse import urlparse

# Contains all clients that connected to dns server
CLIENTS_CONNECTED_RECORD = {}

PLUS_DIVIDER = "+++++++++++++++++++++++++++++++++++++++++++++++\n"

PORT = 40015  # our assigned port
REPLICA_SERVER_DOMAINS = ["p5-http-a.5700.network",
                          "p5-http-b.5700.network",
                          "p5-http-c.5700.network",
                          "p5-http-d.5700.network",
                          "p5-http-e.5700.network",
                          "p5-http-f.5700.network",
                          "p5-http-g.5700.network"]

'''
idea instead of geocache we could send a ping from DNS and spoof the ICMP packet's
recieving ip address to be the ip address of every replica server
Then just have the replica server constantly listenign for ICMP packets
and if the ICMP packet is received by it then send the time received to DNS
Keep in mind, time zone diff and time ICMP was sent, also maybe send 4 ICMP packets
and get the avg RTT of each one???
'''


class DNSServer:
    def __init__(self, dns_port: int, customer_name: str,
                 display: bool = False, display_geo_load: bool = False) -> None:

        self.replica_ips = {}
        self.customer_name = customer_name

        for each in REPLICA_SERVER_DOMAINS:
            try:
                self.replica_ips[each] = socket.gethostbyname(each)
            except socket.gaierror:
                if display == True:
                    print(f"Replica server: {each} UNAVAILABLE")
                continue

        if display == True:
            print(PLUS_DIVIDER)

        if display == True:
            print("Displaying replica server ips:")
            for key, value in self.replica_ips.items():
                print(f"DOMAIN: {key}\tIP: {value}")
            print(PLUS_DIVIDER)

        self.replica_lat_longs = {}

        # set up geodb
        try:
            self.geoLookup = geo_db(display_geo_load)
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt Occured")
            print("EXITING PROGRAM")
            exit(0)

        for key, value in self.replica_ips.items():
            self.replica_lat_longs[key] = self.geoLookup.getLatLong(value)

        if display == True:
            print("Displaying replica server locations:")
            for geoKey, geoVal in self.replica_lat_longs.items():
                print(f"Domain: {geoKey}\tLocation: {geoVal}")
            print(PLUS_DIVIDER)

        # build the socket
        try:
            # AF_INET means IPV4, DGRAM means UDP, which does not care about reliability
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # TODO DELETE AFTER COMPLETE BUILD THIS ONLY FOR TESTING
            self.dns_ip = self.get_ip_src()
            # code below should be applioed to clinet not dns
            # # check that is valid ip address
            # checkThisIp = self.dns_ip[:7]
            # if "192.168" in checkThisIp:
            #     self.dns_ip = self.get_public_ip()
        except socket.error as e:
            print(e)
            print("Socket error occured, could not build dns server")
            print("EXITING PROGRAM")
            exit(0)
        except KeyboardInterrupt as e:
            print(e)
            print("\nKeyboard Interrupt Occured")
            print("EXITING PROGRAM")
            exit(0)

        # bind the server socket to an ip and port
        try:
            self.sock.bind((self.dns_ip, dns_port))
        except Exception as e:
            print(e)
            self.sock.close()

            if display == True:
                print("ERROR: Could not bind to socket\tFailed to create server")
                print("EXITING PROGRAM")

            exit(0)

        except KeyboardInterrupt:
            self.sock.close()
            print("\nKeyboard Interrupt Occured")
            print("EXITING PROGRAM")
            exit(0)

        if display == True:
            print(f"DNS Server Successfully Initialized\nServer ip: {self.dns_ip}\nServer Port: {PORT}\n"
                  f"Resolver set up for domain: {self.customer_name}")
            print(PLUS_DIVIDER)

    def close_server(self, display_close_msg: bool = False):
        '''
        Closes the dns server properly
        :param display_close_msg: (bool) if true, statements will be printed to the console
        :return: None
        '''
        try:
            self.sock.close()
            if display_close_msg == True:
                print("Closing dns server socket")
                print("EXITING PROGRAM")
            exit(0)
        except KeyboardInterrupt:
            self.sock.close()
            print("\nKeyboard Interrupt Occured")
            print("EXITING PROGRAM")
            exit(0)

    # TODO this method is deprecated, DELETE before final submission
    def get_public_ip(self) -> str:
        '''
        Gets public ip instead of local ip address
        :return: (string) ip as string
        '''
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        return ip

    def get_ip_src(self) -> str:
        '''
        Opens up a socket temporarily to get current IP address
        :return: The IP address of the machine as a string
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_addr = s.getsockname()[0]
        s.close()
        return ip_addr

    # TODO this method is deprecated, DELETE before final submission
    def get_website_query(self, client_packet, display=False):
        parsed_request = DNSRecord.parse(client_packet)
        dns_q = parsed_request.get_q()
        website_query = dns_q.qname.__str__()
        urlParseObj = urlparse(website_query)

        if display == True:
            print("Parsing URL Query:")
            print(f"Query NetLoc: {urlParseObj.netloc}")
            print(f"Query path: {urlParseObj.path}\n")

        return urlParseObj

    # TODO this method deprecated, Delete before final submission
    def parse_client_request(self, client_request):
        target_site = self.get_website_query(client_request)
        return self.make_response(target_site)

    def get_distance_between_two_points(self, client_loc: Tuple[float, float],
                                        replica_loc: Tuple[float, float]):
        '''
        This method determines the distance in KM between
        the client loc and replica loc
        :param client_loc: Tuple(lat,long) - a tuple containing the lat and long of a client machine
        :param replica_loc: Tuple(lat,long) - a tuple containining the lat and long a replica machine
        :return: (float) the distance between the two locations in KM
        '''
        client_lat = client_loc[0]
        client_long = client_loc[1]
        replica_lat = replica_loc[0]
        replica_long = replica_loc[1]

        distance_lat = replica_lat - client_lat
        distance_long = replica_long - client_long

        calc_1 = sin(distance_lat / 2) ** 2 + cos(client_lat) * cos(replica_lat) * sin(distance_long / 2) ** 2
        calc_2 = 2 * asin(sqrt(calc_1))
        return calc_2 * 6371

    def get_closest_replica(self, client_loc: Tuple[float, float], display: bool = False) -> Tuple[float, str]:
        '''
        Calculates the closest replica server to the client
        :param client_loc: Tuple(lat,long) -  a tuple containing the lat and long of a client machine
        :param display: (bool) if statements will print to the console
        :return: Tuple(distance between replica and client, replica ip) - a tuple where the
                    first element is the distance between the client and the closest
                    replica server and the second element is the ip of the closest replica
                    server
        '''
        lst_dist = []

        for key in self.replica_lat_longs.keys():
            lst_dist.append(
                (self.get_distance_between_two_points(client_loc, self.replica_lat_longs[key]), key))

        lst_dist = sorted(lst_dist)

        if display == True:
            print("Displaying distances between replica servers and client:")
            for each in lst_dist:
                print(f"Domain: {each[1]}\tDistance to client: {each[0]}")
            print(PLUS_DIVIDER)

        return lst_dist[0]

    def update_replica_ips(self, display_update: bool = False) -> None:
        '''
        Updates the dictionary of domains:ip and domains:location
            > self.replica_ips - domains:ip
            > self.replica_lat_longs - domains:location
        :param display_update: (bool) if true will print statements to the console
        :return:
        '''

        for each in REPLICA_SERVER_DOMAINS:
            self.replica_ips[each] = socket.gethostbyname(each)

        if display_update == True:
            "UPDATING replica server ips:"
            for key, value in self.replica_ips.items():
                print(f"DOMAIN: {key}\tIP: {value}")
            print(PLUS_DIVIDER)

        for key, value in self.replica_ips.items():
            self.replica_lat_longs[key] = self.geoLookup.getLatLong(value)

        if display_update == True:
            print("UPDATING replica server locations:")
            for geoKey, geoVal in self.replica_lat_longs.items():
                print(f"Domain: {geoKey}\tLocation: {geoVal}")
            print(PLUS_DIVIDER)

    def listen_for_clients(self, display_request: bool = False) -> None:
        '''
        Listens for requests from clients. Sends a DNS response with an
            answer containing the closest replica server to the client ip.
        :param display_request: (bool) if true, statements will be printed to the console
        :return: None
        '''
        try:
            while True:
                if display_request == True:
                    print("DNS server listening for clients\n")


                try:
                    # 512 is byte limit for udp
                    data, client_conn_info = self.sock.recvfrom(512)

                except KeyboardInterrupt:
                    if display_request == True:
                        print("\nKeyboard Interrupt Occured")
                        self.close_server(True)
                    else:
                        print("\nKeyboard Interrupt Occured")
                        self.close_server()

                # ip is first element, port is second
                client_ip = client_conn_info[0]
                client_port = int(client_conn_info[1])
                query = DNSRecord.parse(data)

                if display_request == True:
                    print("RCVD CLIENT REQUEST")
                    print(f"Client ip: {client_ip}")
                    print(f"Client port: {client_port}\n")
                    print("Client DNS query:")
                    print(query, end="\n\n")

                #start building reply
                dns_response = query.reply()

                #allow dig packets to come through
                if self.customer_name not in query.get_q().qname.__str__() and \
                        query.get_q().qname.__str__() != ".":
                    if display_request == True:
                        print(f"Domain of query: {query.get_q().qname.__str__()} not recognized\n"
                              f"Sending NXDOMAIN response to client")
                        print(PLUS_DIVIDER)
                    dns_response.header.rcode = RCODE.NXDOMAIN
                    self.sock.sendto(dns_response.pack(), (client_ip, client_port))
                    continue

                # ---------------------------------------------------------------
                # get closest replica

                # if new client find closest replica and store the pair for future
                # requests, instead of looking for closest replica every time
                if client_ip not in CLIENTS_CONNECTED_RECORD.keys():
                    try:
                        closest_replica = self.get_closest_replica(self.geoLookup.getLatLong(client_ip),
                                                                   display=display_request)

                    except RuntimeError:
                        if display_request == True:
                            print(f"Could not obtain lat/long for NEW CLIENT client ip: {client_ip}")
                            print("Check if client ip is valid")
                            print("Ip's that start with 192.168 are invalid as that is local ip")
                            print("Selecting random ip from among replica servers ip\n")
                        random_replica_domain = REPLICA_SERVER_DOMAINS[random.randint(0, len(REPLICA_SERVER_DOMAINS) - 1)]
                        closest_replica = (0, random_replica_domain)

                    if display_request == True:
                        print(f"Selected closest replica to client is {closest_replica[1]}\n")

                    CLIENTS_CONNECTED_RECORD[client_ip] = closest_replica[1]

                else:
                    closest_replica = CLIENTS_CONNECTED_RECORD[client_ip]

                    if display_request == True:
                        print("REQUEST IS FROM RETURNING CLIENT")
                        print(f"Replica server closest to client is {closest_replica}")

                # ---------------------------------------------------------------------
                # parse client request and send response
                dns_response = query.reply()
                print("query:", query.get_q().qname.__str__())
                answer_section_as_str = query.get_q().qname.__str__() + " 60 " + "A " + self.replica_ips[
                    closest_replica[1]]
                dns_response.add_answer(*RR.fromZone(answer_section_as_str))

                self.sock.sendto(dns_response.pack(), (client_ip, client_port))

                if display_request == True:
                    print(f"SENT RESPONSE:\n{dns_response}")
                    print(PLUS_DIVIDER)

        except KeyboardInterrupt:
            if display_request == True:
                print("\nKeyboard Interrupt Occured")
                self.close_server(True)
            else:
                print("\nKeyboard Interrupt Occured")
                self.close_server()