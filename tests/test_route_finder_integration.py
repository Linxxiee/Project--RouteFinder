import unittest
from unittest.mock import patch, MagicMock
# F401 Fix: Removed unused import 'geocoding'
# W291 Fix: Removed trailing whitespace
from route_finder import _process_route_finder_logic 
from rich.console import Console
from io import StringIO

# --- Simulated API Response Data ---
# 1. Mocked Geocoding Success (for "New York")
MOCK_GEOCODE_SUCCESS = {
    "hits": [{
        "point": {"lat": 40.7128, "lng": -74.0060},
        "name": "New York City",
        "country": "USA",
        "osm_value": "place"
    }]
}

# 2. Mocked Routing Success (A short, successful route)
MOCK_ROUTE_SUCCESS = {
    "paths": [{
        "distance": 10000,  # 10 km
        "time": 600000,    # 10 minutes
        "instructions": [
            {"text": "Start driving", "distance": 1000},
            {"text": "Turn right", "distance": 9000}
        ]
    }]
}


class IntegrationTests(unittest.TestCase):

    # W293 Fix: Removed whitespace from blank lines
    def setUp(self):
        # Set up a fake console to capture print output
        self.console_output = StringIO()
        self.mock_console = Console(file=self.console_output)
        
        # Patch the actual Console with the mock one for all functions
        # This allows us to inspect the text printed by the app
        patcher = patch('route_finder.console', self.mock_console)
        self.addCleanup(patcher.stop)
        patcher.start()

    # We use @patch.object to mock the requests.get() function inside the module
    # Note: We need to set the side_effect for the mocked object.
    @patch('requests.get')
    def test_full_successful_route_integration(self, mock_get):
        
        # Configure the mock to return different data on consecutive calls (API calls)
        mock_get.side_effect = [
            # 1st call (geocoding loc1)
            MagicMock(status_code=200, json=lambda: MOCK_GEOCODE_SUCCESS),
            # 2nd call (geocoding loc2)
            MagicMock(status_code=200, json=lambda: MOCK_GEOCODE_SUCCESS),
            # 3rd call (routing API call)
            MagicMock(status_code=200, json=lambda: MOCK_ROUTE_SUCCESS),
        ]

        # Use @patch('builtins.input') to simulate user interaction
        with patch('builtins.input', side_effect=['car', 'New York', 'Boston']):
            # Execute the core logic
            result = _process_route_finder_logic("fake_key", "fake_url?")
            
            # Assertions:
            self.assertTrue(result, "The function should indicate success (True)")
            self.assertEqual(mock_get.call_count, 3, "Expected 3 API calls.")
            
            # Check the output to ensure the summary was generated (Integration check)
            # W291 Fix: Removed trailing whitespace
            output = self.console_output.getvalue()
            self.assertIn("Distance: 6.2 miles / 10.0 km", output, 
                          "The summary output should contain the calculated distance.")
            self.assertIn("Turn-by-Turn Directions", output, 
                          "The output should contain the directions table title.")
