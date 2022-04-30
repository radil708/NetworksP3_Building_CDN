#!/usr/bin/env python3

import requests
from os.path import exists
import zipfile, gzip
import shutil


ZIP_URL = "https://github.com/sapics/ip-location-db/blob/master/geolite2-city/geolite2-city-ipv4.csv.gz?raw=true"
ZIP_URL_BACKUP = ("https://github.com/radil708/GeoFile/blob/master/geo_info.csv.gz?raw=true")


def download_raw_zip_file(src_url):
    r = requests.get(src_url, stream=True)
    with open("geo-ipv4.csv.zip", "wb") as f:
        for chunk in r.raw.stream(1024, decode_content=False):
            if chunk:
                f.write(chunk)

def main():
    # check if zip file exists
    if not (exists("geo-ipv4.zip")):
        print("MISSING ZIP FILE, ATTEMPTING TO DOWNLOAD FROM PRIMARY SOURCE")

        # Download zip if it doesn't exists
        try:
            download_raw_zip_file(ZIP_URL_BACKUP)
            print("Zip file successfully downloaded")
        except Exception as e:
            print(e)
            print(
                    "FAILED to extract from primary source\n"
                    "ATTEMPTING TO DOWNLOAD FROM SECONDARY SOURCE\n"
                    "==============================================\n"
                )
            try:
                download_raw_zip_file(ZIP_URL_BACKUP)
            except Exception as e:
                print(e)
                print(
                        "FAILED to extract from secondary source\n"
                        f"Please check the urls to see if they contain zip files\n"
                        f"1.) {ZIP_URL}\n"
                        f"2.) {ZIP_URL_BACKUP}"
                        "==============================================\n")
                print(
                    "ZIP FILE DOWNLOAD ERROR; Please run dns in default mode to see debug statements"
                    "default mode cmd you should run: './dnsserver -d 1'\n"
                    "EXITING PROGRAM"
                )
                exit(0)
    #
    # check if csv file exists, if not extract to folder
    if not exists("geo-ipv4.csv"):
        print("CSV File cannot be found, STARTING EXTRACTION of zip")

        try:
            with gzip.GzipFile("geo-ipv4.csv.zip", "r") as zip_ref:
                with open("geo-ipv4.csv", "wb") as f_out:
                    shutil.copyfileobj(zip_ref, f_out)
            print("Successfully extracted csv from zip")
        except Exception as e:
            print(e)
            print("Unable to extract csv from zip")


if __name__ == "__main__":
    main()