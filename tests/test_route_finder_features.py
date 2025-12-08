import unittest
from route_finder import RouteFinder, _process_route_finder_logic
import json
import os


class TestRouteFinderIntegration(unittest.TestCase):
    def setUp(self):
        # Sample graph
        self.graph = {
            "A": {"B": {"distance": 5, "time": 2}},
            "B": {"C": {"distance": 7, "time": 3}},
            "C": {"D": {"distance": 4, "time": 1}},
        }
        self.rf = RouteFinder(self.graph)

        # Temporary JSON file for load_new_data
        self.temp_file = "temp_graph.json"
        new_data = {
            "D": {"E": {"distance": 6, "time": 2}},
            "E": {"F": {"distance": 3, "time": 1}}
        }
        with open(self.temp_file, "w") as f:
            json.dump(new_data, f)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_basic_route_distance(self):
        result = _process_route_finder_logic(self.rf, "A", "C", "distance")
        self.assertEqual(result["path"], ["A", "B", "C"])
        self.assertEqual(result["total_distance"], 12)

    def test_basic_route_time(self):
        result = _process_route_finder_logic(self.rf, "A", "C", "time")
        self.assertEqual(result["path"], ["A", "B", "C"])
        self.assertEqual(result["total_distance"], 5)

    def test_start_equals_end(self):
        result = _process_route_finder_logic(self.rf, "A", "A", "distance")
        self.assertEqual(result["path"], ["A"])
        self.assertEqual(result["total_distance"], 0)

    def test_no_connection(self):
        result = _process_route_finder_logic(self.rf, "A", "Z", "distance")
        self.assertEqual(result["path"], [])
        self.assertEqual(result["total_distance"], float("inf"))

    def test_load_new_data(self):
        success = self.rf.load_new_data(self.temp_file)
        self.assertTrue(success)
        self.assertIn("D", self.rf.graph)
        self.assertIn("E", self.rf.graph)
        self.assertIn("F", self.rf.graph)

        # Verify new route
        result = self.rf.find_route("C", "F", "distance")
        self.assertEqual(result["path"], ["C", "D", "E", "F"])
        self.assertEqual(result["total_distance"], 13)


if __name__ == "__main__":
    unittest.main()
