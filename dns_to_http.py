
import socket
import requests

global CLIENTS_CONNECTED_RECORD
CLIENTS_CONNECTED_RECORD = {}

global CLIENTS_CHECK_RTT
CLIENTS_CHECK_RTT = []

global CLIENT_SOCKETS
CLIENT_SOCKETS = []


PORT = 40015  # our assigned port
REPLICA_SERVER_DOMAINS = [
    "p5-http-a.5700.network",
    "p5-http-b.5700.network",
    "p5-http-c.5700.network",
    "p5-http-d.5700.network",
    "p5-http-e.5700.network",
    "p5-http-f.5700.network",
    "p5-http-g.5700.network",
]
def setup(hostDomain, port,display=False):
    try:
        s_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        domainIP = socket.gethostbyname(hostDomain)
        s_.connect((domainIP,port))
        if display == True:
            print(f"Socket created, connected to host:\n"
                  f"domain:{hostDomain}\n"
                  f"host ip: {domainIP}\n"
                  f"host port: {port}\n")
            print("======================\n")
        return s_
    except Exception as e:
        print(e)
        print("tcp client unable to connect to host\n"
                  f"domain:{hostDomain}\n"
                  f"host ip: {domainIP}\n"
                  f"host port: {port}\n")
        print("======================\n")
        return None

def main():
    global CLIENT_SOCKETS
    # try:
    #     x = requests.get('http://p5-http-a.5700.network:40015',data="PING 15.223.19.203")
    #     print(x.text)
    # except Exception as e:
    #     print(e)
    for each_replica in REPLICA_SERVER_DOMAINS:
        CLIENT_SOCKETS.append(setup(each_replica,40015,True))

    for current_socket in CLIENT_SOCKETS:
        current_socket.send("PING 15.223.19.203".encode())
        data = current_socket.recv(4096)
        print(data)
        print("=============================\n")
    # first = CLIENT_SOCKETS[0]
    # first.send("PING 15.223.19.203".encode())
    # data = first.recv(4096)
    # print(data)
main()
