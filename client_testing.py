import socket

def main(): #
    dns_server_ip = '45.33.90.91'
    dns_server_port = 40015
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((dns_server_ip, dns_server_port))
    s.send(b'test test test') #

    #need to send some query first
    s.close()
main()

