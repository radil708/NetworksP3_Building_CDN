from os.path import exists
from os import getcwd
import zipfile
class geo_db():
    def __init__(self, display=False):
        if not(exists('geo-ipv4.zip')):
            print("MISSING ZIP FILE, EXITING PROGRAM")
            exit(1)

        if not exists('geo-ipv4.csv'):
            with zipfile.ZipFile('geo-ipv4.zip', 'r') as zip_ref:
                zip_ref.extractall(getcwd())
            if display == True:
                print("Extracted geo-ipv4.zip")

        else:
            if display == True:
                print("geo db already exists, continuing program")


        # key will be a tuple of ipv4 addr boundaries and value will be a tuple of lat and long as strings
        self.ipv4_dict = {}

        # need search space for binary search of proper keys
        self.ipv4_search_space = []

        with open(file="geo-ipv4.csv", encoding="utf8", errors="surrogateescape") as raw_csv:
            for line in raw_csv.readlines():
                temp = line.split(",")
                self.ipv4_search_space.append((temp[0], temp[1]))
                self.ipv4_dict[(temp[0], temp[1])] = (temp[-3],temp[-2])

        self.len_search_space = len(self.ipv4_search_space)

        if display == True:
            print("Database Ready")


    def getLatLong(self, ipAddrTarget : str):
        low_pos = 0
        high_pos = self.len_search_space

        while low_pos <= high_pos:

            mid_pos = (high_pos + low_pos) // 2

            current_bounds = self.ipv4_search_space[mid_pos]
            low_bound = current_bounds[0]
            upper_bound = current_bounds[1]

            if current_var == target:
                return True

            if current_var < target:
                low_pos = mid_pos + 1
                continue
            elif current_var > target:
                high_pos = mid_pos - 1
                continue

        return False





