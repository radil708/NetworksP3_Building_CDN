import socket
from dnslib import DNSRecord
from ipdb.geo_db import geo_db
import os
import requests
#import dnslib # Use this to parse dns packets

#TODO replace with actual server data
dict_ip_http_servers = {}
dict_ip_http_servers["example server"] = '1.0.1.225'

CLIENTS_CONNECTED_DICT = {}

PORT = 40015 #DNS commonly uses port 53, but we were assigned port 40015
#TODO replic servers with p5-..network get ip and lat long
# send back ip address of closest replica server

#TODO get ipv4 address comes from geodb object

class DNSServer:
    def __init__(self, display=False) -> None:

        #set up geodb
        self.geoLookup = geo_db(True)

        #AF_INET means IPV4, DGRAM means UDP, which does not care about reliablity
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.dns_ip = self.get_ip_src()

        try:
            self.sock.bind((self.dns_ip, PORT))
        except:
            self.sock.close()
            if display == True:
                print("ERROR: Could not bind to socket\tFailed to create server")
                print("EXITING PROGRAM")
                exit(0)

        if display == True:
            print(f"Server Successfully Initialized\nServer ip: {self.dns_ip}\nServer Port: {PORT}")
            print("+++++++++++++++++++++++++++++++++++++++++++++++")

    def get_public_ip(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        return ip


    def parse_client_request(self, request):
        parsed_request = DNSRecord.parse(request)

        pass

    #TODO delete comments
    # Returns the closest replica server, we store a list of replica server ip's
    # find ip addr of replica server and ip addr of the client
    # implement a listener and then print out the client's ipv4 address and close connection
    # test by opening manually and closing with CTRL + C
    def get_ipv4_address(self):
        pass

    def get_ip_src(self):
        '''
        Opens up a socket temporarily to get current IP address
        :return: The IP address of the machine as a string
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_addr = s.getsockname()[0]
        s.close()
        return ip_addr

    def write(self, data):
        with open('written_file', 'wb') as w:
            w.write(data)


def main():
    dns_server = DNSServer(True)
    while True:
        try:
            # 512 is byte limit for udp
            data, client_conn_info = dns_server.sock.recvfrom(512)
            client_ip = client_conn_info[0]

            # store client data if not already stored
            try:
                if client_ip not in CLIENTS_CONNECTED_DICT.keys():
                    lat, long = dns_server.geoLookup.getLatLong(client_ip)
                    CLIENTS_CONNECTED_DICT[client_ip] = (lat,long)

            except RuntimeError:
                print(f"Could not obtain lat long for client ip {client_ip}")
                print("Continuing to listen")
                continue
            client_port = client_conn_info[1]

            client_packet_parsed = DNSRecord.parse(data)

            #TODO delete
            print("New Client connected")
            print(f"Received Client Request:\nClient ip: {client_ip}\nClient port: {client_port}")
            print(f"client lat = {CLIENTS_CONNECTED_DICT[client_ip][0]}\t long = {CLIENTS_CONNECTED_DICT[client_ip][1]}")
            print(client_packet_parsed)
            exit(0)
        except socket.error:
            break
        print(data,client_ip,client_port)
        print("writing data")
        dns_server.write(data)
        break
    print('shutting down')
main()