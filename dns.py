#!/usr/bin/env python3
import math
import os
import socket
import time
from threading import Thread

from dnslib import DNSRecord, DNSHeader, DNSQuestion, RR, A, RCODE
from typing import Tuple

from geo_db import geo_db
from math import radians, cos, sin, atan2, sqrt
import random


# This will contain a mapping of client ip: replica ip where replica ip is the fastest server for the client
# This needs to be global so it can be accessed by both the main dns thread and by the active measurement thread
global CLIENTS_CONNECTED_RECORD
CLIENTS_CONNECTED_RECORD = {}

# This will be a list of client ips. The active measurement thread will pop off values one by one
# to determine the replica with the fastest RTT to the client ip.
# Needs to be global so it can be accessed by both the main dns thread and by the active measurement thread
global CLIENTS_CHECK_RTT
CLIENTS_CHECK_RTT = []


# Variable representing the active measurement thread
global ACTIVE_MEASUREMENT_THREAD
# boolean that tells the active measurement to keep listening for new clients received
global ACTIVE_THREAD_CONTINUE_BOOL
ACTIVE_THREAD_CONTINUE_BOOL = True
# Both need to be gloab so they can be accessed by both the main dns thread and by the active measurement thread

# List containing all available/running replica server ips
# Needs to be global so it can be accessed by both the main dns thread and by the active measurement thread
global VALID_REPLICA_DOMAINS
VALID_REPLICA_DOMAINS = []

#Dictionary of ip: replica domain
# Needs to be global so it can be accessed by both the main dns thread and by the active measurement thread
global IP_TO_VALID_REP_DOMAIN_DICT
IP_TO_VALID_REP_DOMAIN_DICT = {}

# Print statement separators
PLUS_DIVIDER = "+++++++++++++++++++++++++++++++++++++++++++++++\n"
MINUS_DIVIDER = "----------------------------------------------\n"
EQUALS_DIVIDER = "==============================================\n"

# List containing all domains for http/replica servers that may be used
REPLICA_SERVER_DOMAINS = [
    "p5-http-a.5700.network",
    "p5-http-b.5700.network",
    "p5-http-c.5700.network",
    "p5-http-d.5700.network",
    "p5-http-e.5700.network",
    "p5-http-f.5700.network",
    "p5-http-g.5700.network",
]

#Need for haversin formula for geolocation strategy
EARTH_RADIUS = 6373.0


class ActMeasureThread(Thread):
    '''
    This class will run simultaneously with the dns thread. It will request all available the replica/http servers to run a ping
    check to the client. It will receive all the RTT's from the http servers and determine the http server with the
    fastest RTT to a client. It will then modify the mapping of client ip : replica ip that is used by the dns
    server to keep track of where to send the clients to.
    It is called only once in the dns __init__/constructor method.
    '''


    def __init__(self,hostServerPort, display=False):
        Thread.__init__(self)
        global CLIENTS_CONNECTED_RECORD
        global CLIENTS_CHECK_RTT
        global ACTIVE_THREAD_CONTINUE_BOOL
        global IP_TO_VALID_REP_DOMAIN_DICT

        self.client_sockets = []

        self.display = display
        self.target_http_port = hostServerPort

        if display == True:
            print("Active measurement thread initialized\n")

    def set_up_tcp_sockets(self):
        global VALID_REPLICA_DOMAINS

        for valid_rep_dom in VALID_REPLICA_DOMAINS:
            try:
                s_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                domainIP = socket.gethostbyname(valid_rep_dom)
                s_.connect((domainIP, self.target_http_port))
                if self.display == True:
                    print(f"TCP Client Socket created, connected to host:\n"
                          f"domain:{valid_rep_dom}\n"
                          f"host ip: {domainIP}\n"
                          f"host port: {self.target_http_port}\n")
                    print(EQUALS_DIVIDER)
                self.client_sockets.append(s_)
            except Exception as e:
                if self.display == True:
                    print(e)
                    print("TCP Client unable to connect to host\n"
                          f"domain:{valid_rep_dom}\n"
                          f"host ip: {domainIP}\n"
                          f"host port: {self.target_http_port}\n")
                    print(EQUALS_DIVIDER)
                continue

    def close_all_tcp_sockets(self):
        global VALID_REPLICA_DOMAINS

        if len(self.client_sockets) > 0:
            for i in range(len(VALID_REPLICA_DOMAINS)):
                try:
                    self.client_sockets[i].close()
                    if self.display == True:
                        print(f"Client socket to {VALID_REPLICA_DOMAINS[i]} has been closed")
                except Exception as e:
                    print("Line 107: ", e)
                    if self.display == True:
                        print("Unable to close socket")
            if self.display == True:
                print("Resetting client socket list to empty")
            self.client_sockets = []

        else:
            if self.display == True:
                print("There are not tcp sockets to close")



    #Override run method of threading.Thread super class
    def run(self):
        '''
        This method will get called at the very end of the DNSServer constructor. It starts this thread.
        Its purpose is to use tcp clients to connect with the http servers, get RTT information from them
        and inform the DNSServer which HTTP server has the fastest RTT to the client via the
        CLIENT_CONNECTED_RECORD variable
        :return: None
        '''
        global CLIENTS_CONNECTED_RECORD
        global CLIENTS_CHECK_RTT
        global ACTIVE_THREAD_CONTINUE_BOOL
        global IP_TO_VALID_REP_DOMAIN_DICT

        while ACTIVE_THREAD_CONTINUE_BOOL == True:
            time.sleep(0.3)

            # Check for any new clients
            if len(CLIENTS_CHECK_RTT) > 0:
                client_rtt_list = []
                client_ip = CLIENTS_CHECK_RTT.pop(0)
                self.close_all_tcp_sockets()
                self.set_up_tcp_sockets()

                # if new client present then send a ping request to every valid replica server
                for each_socket in self.client_sockets:
                    try:
                        PING_QUERY = "PING " + client_ip
                        each_socket.send(PING_QUERY.encode())
                        data = each_socket.recv(1024).decode()
                        # close socket after receiving

                        #structure of data/response from http servers
                        # data = PING_RTT replica_ip client_ip RTT_from_replica_to_client
                        #example: PING_RTT 45.33.50.187 15.223.19.203 65.299
                        data_lst = data.split(" ")

                        #tuple appended to client_rtt_list is (rtt as float, client ip, replica ip)
                        client_rtt_list.append((float(data_lst[3]), data_lst[2],data_lst[1]))

                        if self.display == True:
                            print(f"Sent RTT CHECK TO HTTP SERVER {data_lst[1]}")
                            print("data received, closing temporary tcp client")
                            print(f"RTT = {data_lst[3]} to client: {data_lst[2]}")
                            print(MINUS_DIVIDER)

                        each_socket.close()

                    except KeyboardInterrupt:
                        print("\nKeyboardInterrupt Occurred During tcp thread")
                        ACTIVE_THREAD_CONTINUE_BOOL=False
                        print("Attempting to close thread loop")

                    except Exception as e:
                        if self.display == True:
                            print("line 177: ", e )
                            print("Unable to get ping information from replica to client")
                        continue

                # all tcp client sockets have been closed so we should clear the socket list
                self.client_sockets = []

                if self.display == True:
                    print(EQUALS_DIVIDER)

                try:
                    # if there are no elemets in the list go back to start
                    if len(client_rtt_list) == 0:
                        if self.display == True:
                            print("No RRT responses received from any replica server\n")
                        continue

                    else:
                        client_rtt_list.sort(key=lambda x: x[0])
                        shortest_rtt_tuple = client_rtt_list.pop(0)

                        # if the item popped has 999 for a return time, then ping failed
                        # keep current client: replica mapping
                        #TODO consider reappending to list? Maybe first pings failed but
                        # may succeed in the future??
                        if math.isclose(shortest_rtt_tuple[0], 999, abs_tol=2.0):
                            if self.display == True:
                                print("Replica's unable to get ping response from client")
                                print("Maintaining current Client: Replica server mapping")
                            continue
                        else:
                            # there is a fast one
                            if self.display == True:
                                print(f"Fastest rtt {shortest_rtt_tuple[0]} to client {shortest_rtt_tuple[1]} "
                                    f"from replica {IP_TO_VALID_REP_DOMAIN_DICT[shortest_rtt_tuple[2]]}")
                                print(
                                    f"Current replica for client:{shortest_rtt_tuple[1]} is {CLIENTS_CONNECTED_RECORD[shortest_rtt_tuple[1]]}")

                            if CLIENTS_CONNECTED_RECORD[shortest_rtt_tuple[1]] == CLIENTS_CONNECTED_RECORD[shortest_rtt_tuple[1]]:
                                if self.display == True:
                                    print("Current mapped replica to client is the same as replica with fastest RTT")
                                    print(EQUALS_DIVIDER)
                                continue
                            else:
                                if self.display == True:

                                    print(f"Setting to {IP_TO_VALID_REP_DOMAIN_DICT[shortest_rtt_tuple[2]]}")

                                CLIENTS_CONNECTED_RECORD[shortest_rtt_tuple[1]] = IP_TO_VALID_REP_DOMAIN_DICT[shortest_rtt_tuple[2]]


                    if self.display == True:
                        print(PLUS_DIVIDER)


                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt Occurred During tcp thread")
                    ACTIVE_THREAD_CONTINUE_BOOL = False
                    print("Attempting to close thread loop")

                except Exception as e:
                    if self.display == True:
                        print("Line 187: ", e)
                        print("No responses from http pings")
            else:
                continue

        #Exited out of loop so close all sockets
        self.close_all_tcp_sockets()
        return


class DNSServer:
    '''
    This class represents the dns server. It's responsibilities:
    1.) Listen for clients send dns queries
    2.) Maintain a record of the http server that will respond the fastest to a client via the CLIENTS_CONNECTED_RECORD
    3.) Send dns responses to the client

    How to use:
    dns_instance = DNSServer(dns_port_value, customer_name_value, display_value, display_geo_load)
    dns_instance.listen_for_clients()

    '''
    def __init__(
        self,
        dns_port: int,
        customer_name: str,
        display: bool = False,
        display_geo_load: bool = False
    ) -> None:
        '''
        The constructor for the DNSServer class. It sets up the dnsserver and creates a geo_db object which is used
            for geolocation and sets up the ActMeasureThread object which is used for active measurement between
            client and replica servers.
        :param dns_port: (int) port the server should bind to
        :param customer_name: (string) the domain the dns should resolve for.
                i.e. like google.com or northeastern.edu...
        :param display: (bool) if true, this will print status/debug statements to the terminal
        :param display_geo_load: (bool) if true, this will print status/debug statements regarding the geodb
                object to the terminal
        '''

        global CLIENTS_CONNECTED_RECORD
        global CLIENTS_CHECK_RTT
        global ACTIVE_MEASUREMENT_THREAD
        global VALID_REPLICA_DOMAINS
        global ACTIVE_THREAD_CONTINUE_BOOL
        global IP_TO_VALID_REP_DOMAIN_DICT

        self.replica_ips = {}
        self.customer_name = customer_name
        VALID_REPLICA_DOMAINS = []
#
        for each in REPLICA_SERVER_DOMAINS:
            try:
                replica_ip = socket.gethostbyname(each)
                self.replica_ips[each] = replica_ip
                VALID_REPLICA_DOMAINS.append(each)
                IP_TO_VALID_REP_DOMAIN_DICT[replica_ip] = each
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
            self.geoLookup = geo_db(display=display_geo_load)
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
            self.dns_ip = self.get_ip_src()

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
                print("ERROR: Could not bind DNS Server to socket\tFailed to create server")
                print("EXITING PROGRAM")

            exit(0)

        except KeyboardInterrupt:
            self.sock.close()
            print("\nKeyboard Interrupt Occured")
            print("EXITING PROGRAM")
            exit(0)

        if display == True:
            print(
                f"DNS Server Successfully Initialized\nServer ip: {self.dns_ip}\nServer Port: {dns_port}\n"
                f"Resolver set up for domain: {self.customer_name}"
            )
            print(PLUS_DIVIDER)

        ACTIVE_THREAD_CONTINUE_BOOL = True
        ACTIVE_MEASUREMENT_THREAD = ActMeasureThread(dns_port,display)
        ACTIVE_MEASUREMENT_THREAD.daemon = True # thread will die when main thread exits
        ACTIVE_MEASUREMENT_THREAD.start()

    def close_server(self, display_close_msg: bool = False):
        """
        Closes the dns socket, any tcp sockets, and then exits the program
        :param display_close_msg: (bool) if true, statements will be printed to the console
        :return: None
        """
        try:
            self.sock.close()
        except KeyboardInterrupt:
            self.sock.close()
        except Exception as e:
            if display_close_msg == True:
                print(e)
                print("DNS server socket has been closed")

        try:
            ACTIVE_MEASUREMENT_THREAD.close_all_tcp_sockets()
        except KeyboardInterrupt:
            ACTIVE_MEASUREMENT_THREAD.close_all_tcp_sockets()
        except Exception as e:
            if display_close_msg == True:
                print(e)
                print("Active Measurement Thread already closed")

        if display_close_msg == True:
            print("DNS server socket SUCCESSFULLY closed")
            print("All replica server clients SUCCESSFULLY closed")
            print("EXITING PROGRAM")

        exit(0)

    def get_ip_src(self) -> str:
        """
        Opens up a socket temporarily to get current IP address
        :return: The IP address of the machine as a string
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_addr = s.getsockname()[0]
        s.close()
        return ip_addr

    def get_distance_between_two_points(
            self, client_loc: tuple, replica_loc: tuple
    ) -> float:
        """
        This method determines the distance in KM between
        the client loc and replica loc
        :param client_loc: Tuple(lat,long) - a tuple containing the lat and long of a client machine
        :param replica_loc: Tuple(lat,long) - a tuple containining the lat and long a replica machine
        :return: (float) the distance between the two locations in KM
        """
        client_lat = radians(float(client_loc[0]))
        client_long = radians(float(client_loc[1]))
        replica_lat = radians(float(replica_loc[0]))
        replica_long = radians(float(replica_loc[1]))

        distance_lat = replica_lat - client_lat
        distance_long = replica_long - client_long

        calc_1 = (
            sin(distance_lat / 2) ** 2
            + cos(client_lat) * cos(replica_lat) * sin(distance_long / 2) ** 2
        )
        calc_2 = 2 * atan2(sqrt(calc_1), sqrt(1 - calc_1))
        return calc_2 * EARTH_RADIUS

    def get_closest_replica(self, client_loc: tuple, display: bool = False) -> tuple:
        """
        Calculates the closest replica server to the client
        :param client_loc: Tuple(lat,long) -  a tuple containing the lat and long of a client machine
        :param display: (bool) if statements will print to the console
        :return: Tuple(distance between replica and client, replica ip) - a tuple where the
                    first element is the distance between the client and the closest
                    replica server and the second element is the ip of the closest replica
                    server
        """
        lst_dist = []

        for key in self.replica_lat_longs.keys():
            lst_dist.append(
                (
                    self.get_distance_between_two_points(
                        client_loc, self.replica_lat_longs[key]
                    ),
                    key,
                )
            )

        lst_dist = sorted(lst_dist)

        if display == True:
            print("Displaying distances between replica servers and client:")
            for each in lst_dist:
                print(f"Domain: {each[1]}\tDistance to client: {each[0]}")
            print(PLUS_DIVIDER)

        return lst_dist[0]

    def update_replica_ips(self, display_update: bool = False) -> None:
        """
        Updates the dictionary of domains:ip and domains:location
            > self.replica_ips - domains:ip
            > self.replica_lat_longs - domains:location
        :param display_update: (bool) if true will print statements to the console
        :return:
        """
        # TODO update
        VALID_REPLICA_DOMAINS = []

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
        """
        Listens for requests from clients. Sends a DNS response with an
            answer containing the closest replica server to the client ip.
        :param display_request: (bool) if true, statements will be printed to the console
        :return: None
        """
        global CLIENTS_CONNECTED_RECORD

        try:
            while True:
                if display_request == True:
                    print("DNS server listening for clients\n")

                try:
                    # 512 is byte limit for udp
                    data, client_conn_info = self.sock.recvfrom(512)

                except KeyboardInterrupt:
                    ACTIVE_THREAD_CONTINUE_BOOL = False
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

                # start building reply
                dns_response = query.reply()

                # allow dig packets to come through, but send NXdomain response if query
                # domain does not match name
                if (
                    self.customer_name not in query.get_q().qname.__str__()
                    and query.get_q().qname.__str__() != "."
                ):
                    if display_request == True:
                        print(
                            f"Domain of query: {query.get_q().qname.__str__()} not recognized\n"
                            f"This DNS only resolves for the domain: {self.customer_name}\n"
                            f"Sending NXDOMAIN response to client"
                        )
                        print(PLUS_DIVIDER)
                    dns_response.header.rcode = RCODE.NXDOMAIN
                    self.sock.sendto(dns_response.pack(), (client_ip, client_port))
                    continue

                # ---------------------------------------------------------------
                # get closest replica

                # if new client find closest replica and store the pair for future
                # requests, instead of looking for closest replica every time
                if client_ip not in CLIENTS_CONNECTED_RECORD.keys():
                    # add client ip to do RTT checks
                    CLIENTS_CHECK_RTT.append(client_ip)
                    if display_request == True:
                        print(f"Adding {client_ip} to check for active measurement")
                    try:
                        # tuple (distance, replica domain)
                        closest_replica: tuple[float, str] = self.get_closest_replica(
                            self.geoLookup.getLatLong(client_ip),
                            display=display_request
                        )

                    except RuntimeError:
                        if display_request == True:
                            print(
                                f"Could not obtain lat/long for NEW CLIENT client ip: {client_ip}"
                            )
                            print("Check if client ip is valid")
                            print(
                                "Ip's that start with 192.168 are invalid as that is local ip"
                            )
                            print("Selecting random ip from among replica servers ip\n")

                        random_replica_domain = VALID_REPLICA_DOMAINS[
                            random.randint(0, len(VALID_REPLICA_DOMAINS) - 1)
                        ]
                        closest_replica: tuple[float, str] = (0, random_replica_domain)

                    if display_request == True:
                        print(
                            f"Selected best replica for client is {closest_replica[1]}\n"
                        )

                    CLIENTS_CONNECTED_RECORD[client_ip] = closest_replica[1]

                else:
                    # returning client
                    closest_ip = CLIENTS_CONNECTED_RECORD[client_ip]
                    closest_replica: tuple[float, str] = (0.0, closest_ip)

                    if display_request == True:
                        print(f"REQUEST IS FROM RETURNING CLIENT: {client_ip}")
                        print(
                            f"Replica server mapped to returning client is {closest_replica[1]}\n"
                        )

                # ---------------------------------------------------------------------
                # parse client request and send response
                dns_response = query.reply()
                if display_request == True:
                    print("client query:", query.get_q().qname.__str__(),end="\n\n")
                # 60 is TTL
                answer_section_as_str = (
                    query.get_q().qname.__str__()
                    + " 60 "
                    + "A "
                    + self.replica_ips[closest_replica[1]]
                )
                dns_response.add_answer(*RR.fromZone(answer_section_as_str))

                self.sock.sendto(dns_response.pack(), (client_ip, client_port))

                if display_request == True:
                    print(f"SENT RESPONSE:\n{dns_response}")
                    print(PLUS_DIVIDER)

        except KeyboardInterrupt:
            ACTIVE_THREAD_CONTINUE_BOOL = False
            if display_request == True:
                print("\nKeyboard Interrupt Occured")
                self.close_server(True)
            else:
                print("\nKeyboard Interrupt Occured")
                self.close_server()
