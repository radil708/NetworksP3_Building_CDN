import socket

PORT = 53 #DNS commonly uses port 53
#
def get_ip_src():
    '''
    Opens up a socket temporarily to get current IP address
    :return: The IP address of the machine as a string
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]
    s.close()
    return ip_addr

def main():
    #AF_INET means IPV4, DGRAM means UDP, which does not care about reliablity
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    my_ip_addr = get_ip_src()
    sock.bind((my_ip_addr,PORT))

    while True:
        #UDP limited to 512 bytes according to protocol
        data, addr = sock.recvfrom(512)
        print(data)


main()