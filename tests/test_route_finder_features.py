import unittest
from route_finder import RouteFinder


class TestRouteFinderFeatures(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "A": {"B": {"distance": 2, "time": 1}},
            "B": {"C": {"distance": 3, "time": 2}},
        }
        self.rf = RouteFinder(self.graph)

    def test_find_route_distance(self):
        result = self.rf.find_route("A", "C", "distance")
        self.assertEqual(result["path"], ["A", "B", "C"])
        self.assertEqual(result["total_distance"], 5)

    def test_find_route_time(self):
        result = self.rf.find_route("A", "C", "time")
        self.assertEqual(result["total_distance"], 3)

    def test_invalid_nodes(self):
        result = self.rf.find_route("A", "X", "distance")
        self.assertEqual(result["path"], [])
        self.assertEqual(result["total_distance"], float("inf"))


if __name__ == "__main__":
    unittest.main()
