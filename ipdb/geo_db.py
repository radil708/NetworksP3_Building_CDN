from os.path import exists
from os import getcwd,listdir
import zipfile
import os
from ipaddress import IPv4Address

class geo_db():
    def __init__(self, display=False):

        path = None

        # for running on my windows
        if os.name == "nt":
            if not (exists('geo-ipv4.zip')):
                print("MISSING ZIP FILE, EXITING PROGRAM")
                exit(1)

            if not exists('geo-ipv4.csv'):
                if display == True:
                    print('CSV File cannot be found, STARTING EXTRACTION of zip')

                with zipfile.ZipFile('geo-ipv4.zip', 'r') as zip_ref:
                    zip_ref.extractall(getcwd())

                if display == True:
                    print("EXTRACTION COMPLETE")
                else:
                    if display == True:
                        print("geo db already exists, continuing program")

        if os.name == "posix":
            # check that zipfile exists
            # TODO CHANGE THIS WHEN MOVING FILES OUT of folder
            path = getcwd() + '/ipdb/'

            if not(exists(path + 'geo-ipv4.zip')):
                print("MISSING ZIP FILE, EXITING PROGRAM")
                exit(1)

            if not exists(path + 'geo-ipv4.csv'):
                if display == True:
                    print('CSV File cannot be found, STARTING EXTRACTION of zip')
                with zipfile.ZipFile(path + 'geo-ipv4.zip', 'r') as zip_ref:
                    zip_ref.extractall(path)
                if display == True:
                    print("EXTRACTION COMPLETE")

            else:
                if display == True:
                    print("geo db already exists, continuing program")


        # key will be a tuple of ipv4 addr boundaries and value will be a tuple of lat and long as strings
        self.ipv4_dict = {}

        # need search space for binary search of proper keys
        self.ipv4_search_space = []

        if display==True:
            print("Building geodb.. Please Wait")

        if os.name == "posix":
            with open(file=path + "geo-ipv4.csv", encoding="utf8", errors="surrogateescape") as raw_csv:
                for line in raw_csv.readlines():
                    try:
                        temp = line.split(",")
                        self.ipv4_search_space.append((temp[0], temp[1]))
                        self.ipv4_dict[(temp[0], temp[1])] = (temp[-3],temp[-2])
                    except IndexError:
                        print(temp)
                        exit(0)

            self.len_search_space = len(self.ipv4_search_space)

        if os.name == "nt":
            with open(file= "geo-ipv4.csv", encoding="utf8", errors="surrogateescape") as raw_csv:
                for line in raw_csv.readlines():
                    temp = line.split(",")
                    self.ipv4_search_space.append((temp[0], temp[1]))
                    self.ipv4_dict[(temp[0], temp[1])] = (temp[-3], temp[-2])

            self.len_search_space = len(self.ipv4_search_space)


        if display == True:
            print("Build completed, Database Ready")


    def getLatLong(self, ipAddrTarget : str):
        '''
        Obtains the lat and long of the target ip address
        by using binary search on the workspace to find target key
        :param ipAddrTarget: the ip address as a string
        :return: a tuple containing the latitude and longitude values (respectively)
            as strings.
        '''
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

            if target_addr >= IPv4Address(low_bound) and target_addr <= IPv4Address(upper_bound):
                target_key = current_bounds
                flag_found = True
                break

            if target_addr <= IPv4Address(low_bound) and target_addr < IPv4Address(upper_bound):
                high_pos = mid_pos - 1
                continue
            elif target_addr >= IPv4Address(low_bound) and target_addr > IPv4Address(upper_bound):
                low_pos = mid_pos + 1
                continue
        if flag_found == False or target_key == None:
            raise RuntimeError('Could not find Ip address')

        return self.ipv4_dict[target_key]





