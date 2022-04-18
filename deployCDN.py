#!/usr/bin/env python
import os
import sys

KEY = '~/.ssh/'
DNS_NODE = 'p5-dns.5700.network'
BUILD_SERVER = 'cs5700cdnproject.ccs.neu.edu'

def parse_args(args):
    # validate port# and name
    pass

def deploy_dns(name):
    # SCP file to the build server and then SSH into dnsserver to start the dns
    scp_command = f'scp -i {KEY} dnsserver {name}@{BUILD_SERVER}'
    os.system(scp_command)

def deploy_http(name):
    # Deploy httpserver to each replica server
    scp_command = f'scp -i {KEY} httpserver {name}@{BUILD_SERVER}'
    os.system(scp_command)
    
def main():
    args = sys.argv
    port_num, name = parse_args(args)

    deploy_dns(name)
