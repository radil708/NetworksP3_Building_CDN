import os
import sys
keyfile = "~/.ssh/id_rsa"
username = "team_t" #should this be radil?
DNS_NODE = "p5-dns.5700.network"
port = 40015

def main():
    run_command = (
        "ssh -i "
        + keyfile
        + " "
        + username
        + "@"
        + DNS_NODE
        + " './dnsserver -p "
        + port
        + " -n "
        + username
        + "'"
    )

    print(f"Running dns command:\n {run_command}")

    os.system(run_command)
main()