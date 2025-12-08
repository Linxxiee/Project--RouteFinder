# File: tests/test_route_finder_features.py

import unittest
import json
import os
from route_finder import RouteFinder

# --- Mock Data Files for Integration Testing ---
# Create a temporary JSON file to simulate the 'hiwayz_v2' data load
TEST_DATA_PATH = 'test_new_data.json'


class TestRouteFinder(unittest.TestCase):  # E302 fix: Added an extra blank line above the class

    def setUp(self):
        """
        1. Set up a graph with a fixed distance and time metric for testing.
        2. Graph setup: A(0) --[D:10, T:5]--> B(10/5) --[D:5, T:2]--> C(15/7)
           A --[D:100, T:1]--> D --[D:1, T:1]--> C (Total D:101, Total T:2)

        Shortest Distance: A -> B -> C (15)
        Shortest Time: A -> D -> C (2)
        """
        self.initial_graph_data = {
            'A': {'B': {'distance': 10, 'time': 5},
                  'D': {'distance': 100, 'time': 1}},
            'B': {'C': {'distance': 5, 'time': 2}},
            'C': {},
            'D': {'C': {'distance': 1, 'time': 1}}
        }
        self.rf_instance = RouteFinder(self.initial_graph_data)

        # Create mock data file for Feature 1 (Dynamic Node Addition)
        self.new_data = {
            # E261 fix: Added at least two spaces before the inline comment
            'D': {'E': {'distance': 8, 'time': 4}},  # Adds a new connection to existing D
            # E261 fix: Added at least two spaces before the inline comment
            'E': {'F': {'distance': 2, 'time': 1}},  # Adds new node E and F
        }
        with open(TEST_DATA_PATH, 'w') as f:
            json.dump(self.new_data, f)

    def tearDown(self):
        """Clean up the mock data file after all tests run."""
        if os.path.exists(TEST_DATA_PATH):
            os.remove(TEST_DATA_PATH)

    # --- CORE FUNCTIONALITY TESTS ---

    def test_known_route_distance(self):
        """Tests the core algorithm using the distance metric (A->B->C)."""
        result = self.rf_instance.find_route('A', 'C', metric='distance')
        self.assertEqual(result['total_distance'], 15)
        self.assertEqual(result['path'], ['A', 'B', 'C'])

    def test_unreachable_destination(self):
        """Tests case where a node is disconnected."""
        # 'Z' is not in the graph
        result = self.rf_instance.find_route('A', 'Z')
        self.assertEqual(result['total_distance'], float('inf'))
        self.assertEqual(result['path'], [])

    def test_start_equals_end(self):
        """Tests the trivial case of starting and ending at the same node."""
        result = self.rf_instance.find_route('A', 'A')
        self.assertEqual(result['total_distance'], 0)
        self.assertEqual(result['path'], ['A'])

    # --- FEATURE 2: ROUTE OPTIMIZATION BY TIME TESTS ---

    def test_route_by_time_metric(self):
        """Tests the algorithm using the 'time' metric (A->D->C)."""
        # Shortest Time: A (1) -> D (1) -> C. Total Time: 2
        result = self.rf_instance.find_route('A', 'C', metric='time')
        self.assertEqual(result['total_distance'], 2)
        self.assertEqual(result['path'], ['A', 'D', 'C'])

    def test_invalid_metric_fails(self):
        """Tests that using an unsupported metric raises a ValueError."""
        with self.assertRaises(ValueError):
            self.rf_instance.find_route('A', 'C', metric='fuel_cost')

    # --- FEATURE 1: DYNAMIC NODE ADDITION (INTEGRATION) TESTS ---

    def test_load_new_data_integration(self):
        """
        Tests that new nodes/edges are loaded and the pathfinding works
        after the dynamic update.
        """
        initial_node_count = len(self.rf_instance.graph)

        # Load the new data which adds nodes 'E' and 'F'
        success = self.rf_instance.load_new_data(TEST_DATA_PATH)
        self.assertTrue(success)

        # 1. Test graph structure update
        self.assertIn('F', self.rf_instance.graph, "New node 'F' should be present in the graph.")
        self.assertEqual(len(self.rf_instance.graph), initial_node_count + 2, "Graph size should increase by 2.")

        # 2. Test that a route through the new nodes is now possible
        # Check route from A (old node) to F (new node)
        result = self.rf_instance.find_route('A', 'F', metric='distance')

        # Route should be A -> D (100) -> E (8) -> F (2). Total: 110
        self.assertEqual(result['total_distance'], 110)
        self.assertEqual(result['path'], ['A', 'D', 'E', 'F'])


if __name__ == '__main__':
    unittest.main()  # E305 fix: Added two blank lines above this block
