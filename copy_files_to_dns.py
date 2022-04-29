import os
from pathlib import Path

key_path = "~/.ssh/id_rsa"
server = "team_t@p5-dns.5700.network"

DNS_FILE_DEPENDENCIES =['dns.py', 'dnsDriver.py', 'dnsserver', 'geo_db.py']

def run_DNS_make():
    cmd = 'make -f makeDNSServer'
    os.system(cmd)
    print("created ./dnsserver exec")

def run_copy(file_name):
    file_path = os.getcwd() + '/' + file_name
    file_path = Path(file_path)
    #path_to_file = Path.joinpath(Path.cwd(),file_name)
    copy_cmd = f"scp -i {key_path} {file_name} {server}:"
    print(copy_cmd)
    os.system(copy_cmd)
    print(f"Copied {file_name} to {server} ")

def main():
    run_DNS_make()
    for file in DNS_FILE_DEPENDENCIES:
        run_copy(file)
main()

