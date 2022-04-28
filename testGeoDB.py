import unittest
from geo_db import geo_db
import socket
from math import radians, cos, sin, asin, sqrt, atan2

PORT = 40015  # our assigned port
REPLICA_SERVER_DOMAINS = ["p5-http-a.5700.network",
                          "p5-http-b.5700.network",
                          "p5-http-c.5700.network",
                          "p5-http-d.5700.network",
                          "p5-http-e.5700.network",
                          "p5-http-f.5700.network",
                          "p5-http-g.5700.network"]
CLIENT_IPS = ["15.223.19.203",
              "54.207.206.161",
              "52.62.170.156",
              "54.215.100.111",
              "13.234.54.32",
              "54.251.196.47"]

client_lat_long_dict = {}

geoLookup = geo_db()
valid_ips = []
valid_replica_ip_dict = {}
valid_replica_ip_lat_long = {}

for each in REPLICA_SERVER_DOMAINS:
    try:
        valid_replica_ip_dict[each] = socket.gethostbyname(each)
        valid_ips.append(each)
    except socket.gaierror:
        print(f"Replica server: {each} UNAVAILABLE")
        continue

geoLookup = geo_db(True)

for key,value in valid_replica_ip_dict.items():
    valid_replica_ip_lat_long[key] = geoLookup.getLatLong(value)

for each in CLIENT_IPS:
    client_lat_long_dict[each] = geoLookup.getLatLong(each)

print("hello")






def get_distance_between_two_points(client_loc: tuple[float, float],
                                    replica_loc: tuple[float, float]):
    '''
    This method determines the distance in KM between
    the client loc and replica loc
    :param client_loc: Tuple(lat,long) - a tuple containing the lat and long of a client machine
    :param replica_loc: Tuple(lat,long) - a tuple containining the lat and long a replica machine
    :return: (float) the distance between the two locations in KM
    '''
    earth_radius = 6373.0
    client_lat = radians(float(client_loc[0]))
    client_long = radians(float(client_loc[1]))
    replica_lat = radians(float(replica_loc[0]))
    replica_long = radians(float(replica_loc[1]))

    distance_lat = replica_lat - client_lat
    distance_long = replica_long - client_long

    calc_1 = sin(distance_lat / 2) ** 2 + cos(client_lat) * cos(replica_lat) * sin(distance_long / 2) ** 2
    calc_2 = 2 * atan2(sqrt(calc_1), sqrt(1-calc_1))
    return calc_2 * earth_radius


for client_ip, client_loc in client_lat_long_dict.items():
    print(f"Checking distance client ip {client_ip}\t {client_loc}")
    for replica_name, replica_loc in valid_replica_ip_lat_long.items():
        print(f"distance to replica: {replica_name}\t {valid_replica_ip_dict[replica_name]}\t {replica_loc}")
        print(get_distance_between_two_points(client_loc, replica_loc),end="\n\n")
    print("==============================================\n")

# class geoDBTest(unittest.TestCase):
#     def printTest(self):
#         for client_ip,client_loc in client_lat_long_dict.items():
#             print(f"Checking distance client ip {client_ip}\t {client_loc}")
#             for replica_name, replica_loc in valid_replica_ip_lat_long.items():
#                 print(f"distance to replica: {replica_name}\t {valid_replica_ip_dict[replica_name]}\t {replica_loc}")
#                 print(get_distance_between_two_points(client_loc, replica_loc))
#         print("==============================================\n")
#
#
#
#
#
#
#
# if __name__ == "__main__":
#     unittest.main(verbosity=3)