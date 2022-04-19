import unittest
from geo_db import geo_db
class ipdbTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.db = geo_db(True)

    def test_1(cls):
        target_addr = '1.0.0.52'
        lat,long = cls.db.getLatLong(target_addr)
        cls.assertEqual('-27.4767', lat)
        cls.assertEqual('153.017',long)

    def test_2(cls):
        #google ip addr according to ping
        target_addr = '142.251.35.174'
        lat, long = cls.db.getLatLong(target_addr)
        cls.assertEqual('20.5888', lat)
        cls.assertEqual('-100.39', long)

    def test3(cls):
        #choffnes website ip addr according to ping #
        target_addr = '204.44.192.60'
        lat, long = cls.db.getLatLong(target_addr)
        cls.assertEqual('43.4462', lat)
        cls.assertEqual('-79.6686', long)

    def test4(cls):
        # example ip #
        target_addr = '192.168.0.248'
        lat, long = cls.db.getLatLong(target_addr)
        cls.assertEqual('43.4462', lat)
        cls.assertEqual('-79.6686', long)

if __name__ == "__main__":
    unittest.main(verbosity=3)