import random
import os

class ServerSelector:
    def __init__(self) -> None:
        self.client_to_server_dict = {}
        self.all_available_servers = set()
        self.check_servers_for_client = False

    def get_server_for_client(self, client_ip):
        if client_ip in self.client_to_server_dict:
            return self.client_to_server_dict[client_ip]
        else:
            self.check_servers_for_client = True
            return random.choice(self.all_available_servers)

    def add_client(self, client_ip, best_server):
        self.client_to_server_dict[client_ip] = best_server
    
    def ping_all_servers(self, client_ip):
        # Check the latency from client to each replica server
        # Store the data in self.client_to_server_dict using self.add_client
        # Use iPlane dataset for this? 
        if self.check_servers_for_client == False:
            return 
        else:
            os.popen(f"ping {client_ip}").read()
