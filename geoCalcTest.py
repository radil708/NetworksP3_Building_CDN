from math import radians, sin, atan2, sqrt, cos
from typing import Tuple
import unittest


from geo_db import geo_db

# value is (lat, long)
# -lat = south, +lat = north
#-long = west, +long = east

REPLICA_DICT_LOCATION = {"p5-http-a.5700.network": (33.844, -84.4784),
                "p5-http-b.5700.network": (37.5625, -122.0004),
                "p5-http-c.5700.network": (-33.8715, 151.2006),
                "p5-http-d.5700.network": (50.1188, 8.6843),
                "p5-http-e.5700.network": (35.6893, 139.6899),
                "p5-http-f.5700.network": (51.5095, -0.0955),
                "p5-http-g.5700.network": (19.0748, 72.8856)
                         }

REPLICA_DICT_IP = {"p5-http-a.5700.network": "50.116.41.109",
                   "p5-http-b.5700.network": "45.33.50.187",
                   "p5-http-c.5700.network": "194.195.121.150",
                   "p5-http-d.5700.network": "172.104.144.157",
                   "p5-http-e.5700.network": "172.104.110.211",
                   "p5-http-f.5700.network": "88.80.186.80",
                   "p5-http-g.5700.network": "172.105.55.115",
                  }

BEACON_CLIENT_DICT = {"15.223.19.203": (45.4995, -73.5848),
               "54.207.206.161": (-23.5335, -46.6359),
               "52.62.170.156": (-33.8715, 151.2006),
               "54.215.100.111": (37.3388, -121.8916),
               "13.234.54.32":	 (19.0748, 72.8856),
               "54.251.196.47": (1.3036, 103.8554)
               }


def get_distance_between_two_points(client_loc: Tuple[float, float],
                                    replica_loc: Tuple[float, float]):
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

def get_closest_replica(client_loc: Tuple[float, float]) -> Tuple[float, str]:
    """
    Calculates the closest replica server to the client
    :param client_loc: Tuple(lat,long) -  a tuple containing the lat and long of a client machine
    :param display: (bool) if statements will print to the console
    :return: Tuple(distance between replica and client, replica ip) - a tuple where the
                first element is the distance between the client and the closest
                replica server and the second element is the ip of the closest replica
                server
    """
    lst_dist = []

    for key in REPLICA_DICT_LOCATION.keys():
        lst_dist.append(
            (
                get_distance_between_two_points(
                    client_loc, REPLICA_DICT_LOCATION[key]
                ),
                key,
            )
        )

    lst_dist = sorted(lst_dist)

    return lst_dist[0]

GEO_LOOKUP = geo_db(True)

class geoTest(unittest.TestCase):
    def testDistanceCalculations(self):
        print("Testing Distance Calculations")
        calc_distance = get_distance_between_two_points(BEACON_CLIENT_DICT["15.223.19.203"],
                                                        REPLICA_DICT_LOCATION["p5-http-a.5700.network"])
        #print(calc_distance)
        self.assertAlmostEqual(1592, calc_distance,delta=20)

        calc_distance = get_distance_between_two_points(BEACON_CLIENT_DICT["15.223.19.203"],
                                                        REPLICA_DICT_LOCATION["p5-http-b.5700.network"])
        self.assertAlmostEqual(4059, calc_distance, delta=20)
        #print(calc_distance)

        calc_distance = get_distance_between_two_points(BEACON_CLIENT_DICT["15.223.19.203"],
                                                        REPLICA_DICT_LOCATION["p5-http-c.5700.network"])
        self.assertAlmostEqual(16018, calc_distance, delta=20)
        #print(calc_distance)

        calc_distance = get_distance_between_two_points(BEACON_CLIENT_DICT["15.223.19.203"],
                                                        REPLICA_DICT_LOCATION["p5-http-d.5700.network"])
        self.assertAlmostEqual(5842, calc_distance, delta=20)
        #print(calc_distance)

        calc_distance = get_distance_between_two_points(BEACON_CLIENT_DICT["15.223.19.203"],
                                                        REPLICA_DICT_LOCATION["p5-http-e.5700.network"])
        self.assertAlmostEqual(10382, calc_distance, delta=20)
        #print(calc_distance)

        calc_distance = get_distance_between_two_points(BEACON_CLIENT_DICT["15.223.19.203"],
                                                        REPLICA_DICT_LOCATION["p5-http-f.5700.network"])
        self.assertAlmostEqual(5221, calc_distance, delta=20)
        #print(calc_distance)

        calc_distance = get_distance_between_two_points(BEACON_CLIENT_DICT["15.223.19.203"],
                                                        REPLICA_DICT_LOCATION["p5-http-g.5700.network"])
        self.assertAlmostEqual(12069, calc_distance, delta=20)
        #print(calc_distance)

    def testCorrectShortest(self):
        print("Testing Closest Location")
        closest_replica = get_closest_replica(BEACON_CLIENT_DICT["15.223.19.203"])
        closest_replica = closest_replica[1]
        closest_replica_ip = REPLICA_DICT_IP[closest_replica]
        self.assertEqual("50.116.41.109",closest_replica_ip)

        closest_replica = get_closest_replica(BEACON_CLIENT_DICT["54.215.100.111"])
        closest_replica = closest_replica[1]
        closest_replica_ip = REPLICA_DICT_IP[closest_replica]
        self.assertEqual("45.33.50.187", closest_replica_ip)

        closest_replica = get_closest_replica(BEACON_CLIENT_DICT["54.251.196.47"])
        closest_replica = closest_replica[1]
        closest_replica_ip = REPLICA_DICT_IP[closest_replica]
        self.assertEqual("172.105.55.115", closest_replica_ip)


if __name__ == "__main__":
    unittest.main(verbosity=3)
