import socket
import dnslib # Use this to parse dns packets

PORT = 53 #DNS commonly uses port 53

class DNSServer:
    def __init__(self) -> None:
        #AF_INET means IPV4, DGRAM means UDP, which does not care about reliablity
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.dns_ip = self.get_ip_src()
        self.bind_socket()

    def bind_socket(self):
        try:
            self.sock.bind((self.dns_ip,PORT))
        except Exception as e:
            print("Could not bind to socket")

    def parse_client_request(self, request) -> bool:
        # 
        pass

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

    def start_receiving(self):
        while True:
            #UDP limited to 512 bytes according to protocol #
            data, addr = self.sock.recvfrom(512)
            print(data)

def main():
    dns_server = DNSServer()
    dns_server.start_receiving()
main()