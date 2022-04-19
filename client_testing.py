import socket
import requests
from dnslib import DNSRecord

def get_my_ip():
    ip = requests.get('https://api.ipify.org').content.decode('utf8')
    print('My public IP address is: {}'.format(ip))
    print(type(ip))
    return ip

def main():
    dns_server_ip = '192.168.0.248'
    dns_server_port = 40015
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((dns_server_ip, dns_server_port))
    dns_packet = DNSRecord.question("google.com")
    s.send(dns_packet.pack())
    print("SENT")

    #need to send some query first
    s.close()
main()

