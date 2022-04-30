from os.path import exists
from os import getcwd, listdir
import zipfile, gzip
import os
from ipaddress import IPv4Address
import requests
import shutil
import urllib
import tarfile
from time import sleep

ZIP_URL = "https://github.com/sapics/ip-location-db/blob/master/geolite2-city/geolite2-city-ipv4.csv.gz?raw=true"
ZIP_URL_BACKUP = (
    "https://github.com/radil708/GeoFile/blob/master/geo_info.csv.gz?raw=true"
)


def download_raw_zip_file(src_url):
    r = requests.get(src_url, stream=True)
    with open("geo-ipv4.csv.zip", "wb") as f:
        for chunk in r.raw.stream(1024, decode_content=False):
            if chunk:
                f.write(chunk)


def download_gzip(src_url):
    with urllib.request.urlopen(src_url) as response:
        with gzip.GzipFile(fileobj=response) as uncompressed:
            file_content = uncompressed.read()

class geo_db:
    def __init__(self, display=False):

        path = None

        if display == True:
            print("Starting to build geoCache...")

        # check if zip file exists
        if not (exists("geo-ipv4.csv.zip")):
            if display == True:
                print("MISSING ZIP FILE, ATTEMPTING TO DOWNLOAD FROM PRIMARY SOURCE")

            # Download zip if it doesn't exists
            try:
                download_raw_zip_file(ZIP_URL_BACKUP)
                if display == True:
                    print("Zip file successfully downloaded")
            except Exception as e:
                if display == True:
                    print(e)
                    print(
                        "FAILED to extract from primary source\n"
                        "ATTEMPTING TO DOWNLOAD FROM SECONDARY SOURCE\n"
                        "==============================================\n"
                    )
                try:
                    download_raw_zip_file(ZIP_URL_BACKUP)
                except Exception as e:
                    if display == True:
                        print(e)
                        print(
                            "FAILED to extract from secondary source\n"
                            f"Please check the urls to see if they contain zip files\n"
                            f"1.) {ZIP_URL}\n"
                            f"2.) {ZIP_URL_BACKUP}"
                            "==============================================\n"
                        )
                    print(
                        "ZIP FILE DOWNLOAD ERROR; Please run dns in default mode to see debug statements"
                        "default mode cmd you should run: './dnsserver -d 1'\n"
                        "EXITING PROGRAM"
                    )
                    exit(0)
        else:
            if display == True:
                print("Zip file Present, Proceeding...")
                print("+++++++++++++++++++++++++++++++++++++++++\n")
        #
        # check if csv file exists, if not extract to folder
        if not exists("geo-ipv4.csv"):
            if display == True:
                print("CSV File cannot be found, STARTING EXTRACTION of zip")

            with gzip.GzipFile("geo-ipv4.csv.zip", "r") as zip_ref:
                with open("geo-ipv4.csv", "wb") as f_out:
                    shutil.copyfileobj(zip_ref, f_out)

            if display == True:
                print("EXTRACTION COMPLETE")
                print("+++++++++++++++++++++++++++++++++++++++++\n")
        else:
            if display == True:
                print("geozip file already exists, Proceeding...")
                print("+++++++++++++++++++++++++++++++++++++++++\n")

        # key will be a tuple of ipv4 addr boundaries and value will be a tuple of lat and long as strings
        self.ipv4_dict = {}

        # need search space for binary search of proper keys
        self.ipv4_search_space = []

        if display == True:
            print("Building geoCache.. Please Wait")

        with open(
            file="geo-ipv4.csv", encoding="utf8", errors="surrogateescape"
        ) as raw_csv:
            for line in raw_csv.readlines():
                try:
                    temp = line.split(",")
                    self.ipv4_search_space.append((temp[0], temp[1]))
                    self.ipv4_dict[(temp[0], temp[1])] = (
                        float(temp[-3]),
                        float(temp[-2]),
                    )
                except IndexError:
                    print(temp)
                    exit(0)
                except KeyboardInterrupt:
                    print("\nKeyboard Interrupt Occured")
                    print("EXITING PROGRAM")
                    exit(0)

            self.len_search_space = len(self.ipv4_search_space)

        if display == True:
            print("Build completed, geoCache Ready")
            print("++++++++++++++++++++++++++++++++++++++++\n")

    def getLatLong(self, ipAddrTarget: str):
        """
        Obtains the lat and long of the target ip address
        by using binary search on the workspace to find target key
        :param ipAddrTarget: the ip address as a string
        :return: a tuple containing the latitude and longitude values (respectively)
            as strings.
        """
        low_pos = 0
        high_pos = self.len_search_space
        target_addr = IPv4Address(ipAddrTarget)

        flag_found = False
        target_key = None

        while low_pos <= high_pos:

            mid_pos = (high_pos + low_pos) // 2

            current_bounds = self.ipv4_search_space[mid_pos]
            low_bound = current_bounds[0]
            upper_bound = current_bounds[1]

            if target_addr >= IPv4Address(low_bound) and target_addr <= IPv4Address(
                upper_bound
            ):
                target_key = current_bounds
                flag_found = True
                break

            if target_addr <= IPv4Address(low_bound) and target_addr < IPv4Address(
                upper_bound
            ):
                high_pos = mid_pos - 1
                continue
            elif target_addr >= IPv4Address(low_bound) and target_addr > IPv4Address(
                upper_bound
            ):
                low_pos = mid_pos + 1
                continue
        if flag_found == False or target_key == None:
            raise RuntimeError("Could not find Ip address")

        return self.ipv4_dict[target_key]
