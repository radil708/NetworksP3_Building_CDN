import socket
import requests
from dnslib import DNSRecord

DNS_SERVER_TARGET_IP = '192.168.0.248'
#DNS_SERVER_TARGET_IP  = '45.33.90.91'
DNS_SERVER_TARGET_PORT = 40015
VALID_EXAMPLE_QUERY = "http://cs5700cdnorigin.ccs.neu.edu:8080/Aaron_Hernandez"
INVALID_EXAMPLE_QUERY = "https://david.choffnes.com/"
class client():
    def __init__(self, display_set_up = False):
        # set up udp socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.connect((DNS_SERVER_TARGET_IP, DNS_SERVER_TARGET_PORT))
        except socket.error as e:
            print(e)
            print("Client is unable to bind to target sock server")
            self.close_client(display_set_up)

        if display_set_up == True:
            print("Client successfully connected to server")
            print(f"Server ip: {DNS_SERVER_TARGET_IP}\nServer Port: {DNS_SERVER_TARGET_PORT}")
            print("++++++++++++++++++++++++++\n")



    def get_client_ip(self, displayIp=False):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        if displayIp == True:
            print('Client IP address is: {}'.format(ip))
        return ip

    def close_client(self, display_close_msg=False):
        self.sock.close()

        if display_close_msg == True:
            print("Client socket closed")
            print("EXITING PROGRAM")
        exit(0)

    def send_dns_query(self, website_query, display_sent_query):
        dns_packet = DNSRecord.question(website_query)
        if display_sent_query == True:
            print("Sending UDP Query")
            print(dns_packet)
        self.sock.send(dns_packet.pack())

def main():
    x = client(True)
    x.send_dns_query(VALID_EXAMPLE_QUERY,True)
    print("++++++++++++++++++++++++++++++++++++\n")
    x.send_dns_query(INVALID_EXAMPLE_QUERY,True)
    x.close_client(True)
main()


