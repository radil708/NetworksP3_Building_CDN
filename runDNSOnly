#!/usr/bin/env python3
import os
import sys
keyfile = "~/.ssh/id_rsa"
username = "team_t" #should this be radil?
DNS_NODE = "p5-dns.5700.network"
domainName = "cs5700cdn.example.com"
port = '40015'

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
        + domainName
        + "'"
    )

    print(f"Running dns command:\n {run_command}")

    os.system(run_command)
main()