#!/usr/bin/env python3
import os
import sys

keyfile = "~/.ssh/id_rsa"
username = "radil" #should this be radil?
DNS_NODE = "p5-dns.5700.network"
port = '40015'


def main():
    ssh_command = (
            "ssh -i "
            + keyfile
            + " "
            + username
            + "@"
            + DNS_NODE
            + " 'pkill -u "
            + username
            + " dnsserver'"
    )

    print(f"Running kill command:\n {ssh_command}")

    os.system(ssh_command)


main()