import socket
import requests
from dnslib import DNSRecord

def get_my_ip():
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    print('My public IP address is: {}'.format(ip))
    print(type(ip))
    return ip

#ip of server = 45.33.90.91
#ip of personal com = '192.168.0.248'
def main():
    dns_server_ip = '45.33.90.91'
    dns_server_port = 40015
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((dns_server_ip, dns_server_port))
    dns_packet = DNSRecord.question("google.com")
    s.send(dns_packet.pack())
    print("SENT")
    while True:
        data = s.recv(4096)
        print("DATA RECEIVED")
        print(DNSRecord.parse(data))

    #need to send some query first
    s.close()
main()

