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
        "distance": 10000,
        "time": 600000,
        "instructions": [
            {"text": "Start driving", "distance": 1000},
            {"text": "Turn right", "distance": 9000}
        ]
    }]
}


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        self.console_output = StringIO()
        self.mock_console = Console(file=self.console_output)

        patcher = patch('route_finder.console', self.mock_console)
        self.addCleanup(patcher.stop)
        patcher.start()

    @patch('requests.get')
    def test_full_successful_route_integration(self, mock_get):
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: MOCK_GEOCODE_SUCCESS),
            MagicMock(status_code=200, json=lambda: MOCK_GEOCODE_SUCCESS),
            MagicMock(status_code=200, json=lambda: MOCK_ROUTE_SUCCESS),
        ]

        with patch('builtins.input', side_effect=['car', 'New York', 'Boston']):
            result = _process_route_finder_logic("fake_key", "fake_url?")

            self.assertTrue(result, "The function should indicate success (True)")
            self.assertEqual(mock_get.call_count, 3, "Expected 3 API calls.")

            output = self.console_output.getvalue()
            self.assertIn("Distance: 6.2 miles / 10.0 km", output)
            self.assertIn("Turn-by-Turn Directions", output)
