import socket

def main():
    dns_server_ip = 'x'
    dns_server_port = 53
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((dns_server_ip, dns_server_port))
    s.send(b'test test test')

    #need to send some query first
    s.close()
main()
