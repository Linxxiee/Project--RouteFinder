import unittest
from unittest.mock import patch, MagicMock
from route_finder import _process_route_finder_logic
from rich.console import Console
from io import StringIO

# --- Simulated API Response Data ---

MOCK_GEOCODE_SUCCESS = {
    "hits": [{
        "point": {"lat": 40.7128, "lng": -74.0060},
        "name": "New York City",
        "country": "USA",
        "osm_value": "place"
    }]
}

MOCK_ROUTE_SUCCESS = {
    "paths": [{
        "distance": 10000,  # 10 km
        "time": 600000,   # 10 minutes
        "instructions": [
            {"text": "Start driving", "distance": 1000},
            {"text": "Turn right", "distance": 9000}
        ]
    }]
}


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.console_output = StringIO()
        # Ensure the mock console uses the StringIO buffer
        self.mock_console = Console(file=self.console_output)

        # Patch the console used in route_finder.py
        patcher = patch('route_finder.console', self.mock_console)
        self.addCleanup(patcher.stop)
        patcher.start()

    @patch('requests.get')
    def test_full_successful_route_integration(self, mock_get):
        # Program the mock to return geocode, geocode, then route success
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: MOCK_GEOCODE_SUCCESS),
            MagicMock(status_code=200, json=lambda: MOCK_GEOCODE_SUCCESS),
            MagicMock(status_code=200, json=lambda: MOCK_ROUTE_SUCCESS),
        ]

        # Simulate user input: vehicle='car', start='New York', end='Boston'
        with patch('builtins.input', side_effect=['car', 'New York', 'Boston']):
            # The key and url here should ideally match the global variables in route_finder.py
            result = _process_route_finder_logic("fake_key", "fake_url?")  # E261 FIX

            self.assertTrue(result, "The function should indicate success (True)")
            self.assertEqual(mock_get.call_count, 3, "Expected 3 API calls.")

            # Check console output
            output = self.console_output.getvalue()
            # 10000m = 6.2 miles / 10.0 km
            self.assertIn("Distance: 6.2 miles / 10.0 km", output)  # E261 FIX
            self.assertIn("Turn-by-Turn Directions", output)
            self.assertIn("Duration: 00:10:00", output)  # 600,000ms = 10 minutes
