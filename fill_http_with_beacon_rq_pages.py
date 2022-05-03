#!/usr/bin/env python3

import argparse
import pandas as pd
from automated_testing import REPLICA_DICT_IP, MINUS_DIVIDER, EQUALS_DIVIDER
import requests

DEFAULT_PORT = 40015

'''
This file is used for our speed testing and is not involved in [deploy|run|stop]CND for the submission
'''
def run(port_in: int, display: bool = False) -> None:
    beacon_testing_pages = ['Main_Page', '-', 'India', 'Coronavirus', 'Doja_Cat']

    for key in REPLICA_DICT_IP.keys():
        target_ip = REPLICA_DICT_IP[key]
        total_page_request_len = len(beacon_testing_pages)
        quarter_amt_abs = total_page_request_len // 4
        quarter_tracker = total_page_request_len // 4
        percent_counter = 25
        counter = 0

        for each_page in beacon_testing_pages:
            if counter == quarter_tracker:
                quarter_tracker += quarter_amt_abs
                if display == True:
                    print(f"Progressed through {percent_counter}% of requests")
                percent_counter += 25

            request_query = f'http://{target_ip}:{port_in}/{each_page}'

            try:
                requested_page = requests.get(request_query)
                status_code_rcvd = requested_page.status_code
                if display == True:
                    print(f"Succesfully Requested {each_page} from {target_ip} with status code = {status_code_rcvd}")
                    print(MINUS_DIVIDER)
            except requests.exceptions.ConnectionError:
                if display == True:
                    print(f"Possible Query Error: \n{request_query}")
                    print(f"Page may be invalid for {each_page}, Unable to request")
                    print(MINUS_DIVIDER)

        if display == True:
            print(f"Done filling {key} server with small testing cache")
            print(EQUALS_DIVIDER)

    if display == True:
        print("DONE FILLING BEACON CACHE")
        print("EXITING PROGRAM")

def make_parser():
    parser = argparse.ArgumentParser(description="Parser for httpserver args")
    parser.add_argument(
        "-p",
        "--port",
        metavar="",
        type=int,
        help="Port that the http requests will go to",
    )
    parser.add_argument(
        "-s",
        "--display",
        metavar="",
        help="display flag, if not None, will print statements to the terminal",
    )
    return parser

def main():
    parser = make_parser()
    args = parser.parse_args()

    target_port = None
    display_var = False

    #default run
    if args.port == None:
        target_port = DEFAULT_PORT
        display_var = True
    else:
        target_port = args.port
        if args.display is not None:
            display_var = True

    run(target_port, display_var)

if __name__ == "__main__":
    main()


