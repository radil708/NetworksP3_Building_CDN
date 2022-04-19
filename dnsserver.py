import socket
import dnslib # Use this to parse dns packets

PORT = 53 #DNS commonly uses port 53

#TODO get ipv4 address comes from geodb object

class DNSServer:
    def __init__(self, display=False) -> None:
        if display == True:
            print("INITIALIZING DNS SERVER")

        #AF_INET means IPV4, DGRAM means UDP, which does not care about reliablity
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.dns_ip = self.get_ip_src()
        self.bind_socket()

        if display == True:
            print(f"Server ip: {self.dsn_ip}\nServer Port: {PORT}")
            print("+++++++++++++++++++++++++++++++++++++++++++++++")

    def bind_socket(self): #
        self.sock.bind((self.dns_ip,PORT))
        print("Could not bind to socket")
        print("EXITING PROGRAM")
        exit(0)

    def parse_client_request(self, request) -> bool:
        # 
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

    def start_receiving(self):
        try:
            while True:
                #UDP limited to 512 bytes according to protocol #
                data, addr = self.sock.recvfrom(512)
                print(data)
        except KeyboardInterrupt:
            print("EXITING PROGRAM")
            exit(0)

def main():
    dns_server = DNSServer()
    dns_server.start_receiving()
main()