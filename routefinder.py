import webview
import requests
import json
import urllib.parse
import polyline # Make sure you have 'pip install polyline'

# 1. THE PYTHON BACKEND API (No changes)
class Api:
    
    # ---------------------------------------------------------------
    # --- PASTE YOUR GRAPHHOPPER API KEY HERE ---
    # ---------------------------------------------------------------
    API_KEY = "27b08998-f69b-4d43-a3a6-3b4fda277646"
    # ---------------------------------------------------------------


    def __init__(self):
        if self.API_KEY == "27b08998-f69b-4d43-a3a6-3b4fda277646":
            print("="*50)
            print("WARNING: API key is not set in the code.")
            print("Please get a free key from graphhopper.com")
            print("and paste it into the 'API_KEY' variable.")
            print("="*50)

    def get_coordinates(self, place_name):
        """
        Helper function to turn a name into coordinates AND get the full address
        using the GraphHopper Geocoding API.
        """
        try:
            url = "https://graphhopper.com/api/1/geocode"
            params = {
                'q': place_name,
                'key': self.API_KEY,
                'limit': 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or not data.get('hits'):
                raise Exception("Location not found")
            
            hit = data['hits'][0]
            
            address_parts = [hit.get('name'), hit.get('city'), hit.get('state'), hit.get('country')]
            full_address = ', '.join(part for part in address_parts if part)

            return {
                'coords': [hit['point']['lat'], hit['point']['lng']],
                'address': full_address
            }
            
        except Exception as e:
            print(f"Geocode Error: {e}")
            return None

    def zoom_to_place(self, place_name):
        """
        Gets the coordinates for a single place to zoom the map.
        """
        try:
            if not place_name:
                return json.dumps({"error": "No place name provided."})
                
            data = self.get_coordinates(place_name) 
            
            if data:
                return json.dumps({
                    "status": "success",
                    "coords": data['coords']
                })
            else:
                return json.dumps({"error": "Location not found."})
                
        except Exception as e:
            print(f"Zoom Error: {e}")
            return json.dumps({"error": str(e)})

    def get_directions(self, origin_name, destination_name, mode):
        """
        Gets the full route between two place names using GraphHopper.
        """
        try:
            if self.API_KEY == "PASTE_YOUR_GRAPHHOPPER_KEY_HERE":
                return json.dumps({"error": "API Key is not set in the Python code."})

            origin_data = self.get_coordinates(origin_name)
            dest_data = self.get_coordinates(destination_name)
            
            if not origin_data or not dest_data:
                return json.dumps({"error": "Could not find one or both locations."})
            
            origin_coords = origin_data['coords'] # [lat, lon]
            dest_coords = dest_data['coords'] # [lat, lon]

            api_mode = {
                "Driving": "car",
                "Walking": "foot",
                "Bicycling": "bike"
            }.get(mode, "car")

            url = "https://graphhopper.com/api/1/route"
            params = {
                'point': [f"{origin_coords[0]},{origin_coords[1]}", f"{dest_coords[0]},{dest_coords[1]}"],
                'vehicle': api_mode,
                'key': self.API_KEY,
                'instructions': 'true',
                'geometries': 'polyline', # We use polyline
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if 'message' in data:
                 return json.dumps({"error": data['message']})
            
            path = data['paths'][0]
            
            steps = []
            for step in path['instructions']:
                steps.append({
                    "text": step['text'],
                    "sign": step.get('sign', 0)
                })

            decoded_polyline = polyline.decode(path['points'])

            return json.dumps({
                "status": "success",
                "origin_address": origin_data['address'],
                "origin_coords": origin_coords,
                "destination_address": dest_data['address'],
                "destination_coords": dest_coords,
                "polyline_coords": decoded_polyline,
                "steps": steps,
                "distance": f"{path['distance'] / 1000:.1f} km",
                "duration": f"{path['time'] / 60000:.0f} min"
            })

        except Exception as e:
            print(f"Directions Error: {e}")
            if "401" in str(e):
                 return json.dumps({"error": "Invalid API Key. Please check your key."})
            if "400" in str(e):
                return json.dumps({"error": "No route found. This app only supports land routes."})
            return json.dumps({"error": "An error occurred. Check your internet connection."})

# 2. THE HTML, CSS, AND JAVASCRIPT FRONTEND
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GraphHopper Land Route Directions</title>
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* --- Color Variables --- */
        :root {
            /* Light Mode (Default) */
            --bg-color: #ffffff;
            --bg-color-translucent: rgba(255, 255, 255, 0.85);
            --text-primary: #1d1d1f;
            --text-secondary: #515154;
            --accent-blue: #0070e1;
            --accent-blue-hover: #0077ed;
            --border-color: #d2d2d7;
            --map-line: #0070e1;
            --map-glow: #0070e1;
            --shadow-color: rgba(0,0,0,0.1);
        }

        body.dark-mode {
            /* Dark Mode Overrides */
            --bg-color: #2c2c2e;
            --bg-color-translucent: rgba(44, 44, 46, 0.85);
            --text-primary: #f5f5f7;
            --text-secondary: #8e8e93;
            --accent-blue: #0A84FF;
            --accent-blue-hover: #0070e1;
            --border-color: #48484a;
            --map-line: #0A84FF;
            --map-glow: #00f2ff;
            --shadow-color: rgba(0,0,0,0.3);
        }
        /* --- End Color Variables --- */
    
        body, html {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
            background-color: #f0f0f0; /* Light fallback bg */
        }
        
        body.dark-mode {
             background-color: #1c1c1e; /* Dark fallback bg */
        }
        
        #map {
            height: 100%;
            width: 100%;
            background-color: var(--bg-color);
        }
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }

        #control-panel {
            position: absolute;
            top: 15px;
            left: 15px;
            z-index: 1000;
            
            background: var(--bg-color-translucent);
            backdrop-filter: blur(10px); 
            -webkit-backdrop-filter: blur(10px);
            
            border-radius: 12px;
            box-shadow: 0 8px 32px var(--shadow-color);
            border: 1px solid var(--border-color);
            
            width: 360px;
            max-height: calc(100% - 30px);
            display: flex;
            flex-direction: column;
            color: var(--text-primary);
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }
        
        .panel-header {
            padding: 20px 20px 10px 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: border-color 0.3s ease;
        }
        .panel-header h1 {
            font-size: 22px;
            font-weight: 600;
            margin: 0;
        }
        
        .panel-form {
            padding: 20px;
        }
        
        .input-group {
            margin-bottom: 10px;
        }
        .input-group input, .input-group select {
            width: 100%;
            padding: 10px;
            font-size: 15px;
            
            background-color: rgba(120,120,128,0.12); /* Semi-transparent bg */
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            
            border-radius: 8px;
            box-sizing: border-box; 
            margin: 0;
            height: 42px; 
            font-family: 'Inter', sans-serif;
            transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
        }
        .input-group input::placeholder {
            color: var(--text-secondary);
        }
        
        #get-directions-btn {
            background-color: var(--accent-blue);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
            transition: background-color 0.2s ease;
        }
        #get-directions-btn:hover {
            background-color: var(--accent-blue-hover);
        }
        #get-directions-btn:disabled {
            background-color: var(--border-color);
            color: var(--text-secondary);
            cursor: not-allowed;
        }

        .panel-content {
            padding: 20px;
            overflow-y: auto;
            flex: 1; 
        }
        
        #location-display {
            font-size: 14px;
            margin-bottom: 15px;
            line-height: 1.5;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
            transition: border-color 0.3s ease;
        }
        #location-display div {
            padding-bottom: 8px;
        }
        #location-display strong {
            color: var(--text-primary);
            font-weight: 600;
        }
        #location-display div:last-child {
            padding-bottom: 0;
        }

        #summary {
            font-size: 20px;
            font-weight: 500;
            color: var(--text-primary);
            margin: 0 0 15px 0;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
            text-align: center;
            transition: border-color 0.3s ease, color 0.3s ease;
        }
        #summary.error {
            color: #ff4d4d;
            font-size: 16px;
            font-weight: 500;
            text-align: left;
            margin-top: 0;
        }
        
        #mode-icon {
            font-size: 2.5em;
            display: block;
            margin-bottom: 10px;
        }
        
        #steps-list {
            list-style: decimal;
            padding-left: 20px;
            margin: 0;
            font-size: 14px;
            color: var(--text-secondary);
        }
        #steps-list li {
            margin-bottom: 12px;
            line-height: 1.5;
            padding-left: 5px;
            color: var(--text-primary);
            transition: color 0.3s ease;
        }
        #steps-list .icon {
            margin-right: 8px;
            font-size: 1.2em;
            display: inline-block;
            width: 20px;
            text-align: center;
            color: var(--accent-blue);
            transition: color 0.3s ease;
        }
        
        /* --- CSS Loading Spinner --- */
        #loader {
            display: none;
            margin: 10px auto;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--accent-blue);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* --- Animated Icon Toggle CSS --- */
        #theme-toggle-container {
            position: relative;
            width: 24px;
            height: 24px;
        }
        .theme-label {
            cursor: pointer;
            display: block;
            width: 24px;
            height: 24px;
        }
        #theme-toggle {
            display: none;
        }
        .sun-icon, .moon-icon {
            position: absolute;
            top: 0;
            left: 0;
            width: 24px;
            height: 24px;
            stroke: var(--text-primary);
            transition: opacity 0.3s ease, transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .moon-icon {
            fill: var(--text-primary);
            stroke: none;
            opacity: 0;
            transform: rotate(90deg) scale(0);
        }
        .sun-icon {
            fill: none;
            opacity: 1;
            transform: rotate(0deg) scale(1);
        }
        body.dark-mode .sun-icon {
            opacity: 0;
            transform: rotate(-90deg) scale(0);
        }
        body.dark-mode .moon-icon {
            opacity: 1;
            transform: rotate(0deg) scale(1);
        }

        /* --- Leaflet Control Positioning Fix --- */
        .leaflet-control-container {
            right: 15px; 
            left: unset; 
        }
        
        /* --- THIS IS THE FIX: Changed to bottomright --- */
        .leaflet-bottom.leaflet-right {
            bottom: 15px; 
            right: 15px;
        }
        .leaflet-right .leaflet-control-zoom {
            margin-right: 360px;
            transition: margin-right 0.3s ease;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background-color: var(--bg-color-translucent);
            backdrop-filter: blur(10px); 
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px var(--shadow-color);
            color: var(--text-primary);
        }
        .leaflet-right .leaflet-control-zoom a {
            color: var(--text-primary);
            background-color: transparent;
            border-bottom: 1px solid var(--border-color);
        }
        .leaflet-right .leaflet-control-zoom a:first-child {
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        .leaflet-right .leaflet-control-zoom a:last-child {
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            border-bottom: none;
        }
        .leaflet-right .leaflet-control-zoom a:hover {
            background-color: rgba(120,120,128,0.12);
        }
        .leaflet-bottom.leaflet-left {
            bottom: 15px;
            left: 15px;
            margin-left: 360px;
            transition: margin-left 0.3s ease;
            color: var(--text-secondary);
            border-radius: 8px;
            background-color: var(--bg-color-translucent);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px var(--shadow-color);
            padding: 5px 10px;
            border: 1px solid var(--border-color);
        }
        .leaflet-bottom.leaflet-left a {
            color: var(--text-secondary);
        }
        
    </style>
</head>
<body>
    <div id="map"></div>

    <div id="control-panel">
        <div class="panel-header">
            <h1>Directions</h1>
            <div id="theme-toggle-container">
                <input type="checkbox" id="theme-toggle" />
                <label for="theme-toggle" class="theme-label">
                    <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                    <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                </label>
            </div>
        </div>
        
        <div class="panel-form">
            <div class="input-group">
                <input type="text" id="origin" placeholder="Origin (e.g., Manila)">
            </div>
            
            <div class="input-group">
                <input type="text" id="destination" placeholder="Destination (e.g., Baguio)">
            </div>
            
            <div class="input-group">
                <select id="mode">
                    <option>Driving</option>
                    <option>Walking</option>
                    <option>Bicycling</option>
                    <option>Transit</option>
                    <option>Truck</option>
                </select>
            </div>
            <button id="get-directions-btn" disabled>Loading Map...</button>
        </div>
        
        <div class="panel-content">
            <div id="location-display">
                <div id="origin-location"></div>
                <div id="destination-location"></div>
            </div>
            <div id="summary">
                <span id="mode-icon"></span>
                <span id="summary-text">Enter an origin and destination.</span>
                <div id="loader"></div> 
            </div>
            
            <ol id="steps-list">
                </ol>
        </div>
    </div>

    <script>
        const button = document.getElementById('get-directions-btn');
        const summaryDiv = document.getElementById('summary');
        const summaryText = document.getElementById('summary-text');
        const modeIcon = document.getElementById('mode-icon');
        const stepsList = document.getElementById('steps-list');
        const originInput = document.getElementById('origin');
        const destInput = document.getElementById('destination');
        const modeSelect = document.getElementById('mode');
        const originDiv = document.getElementById('origin-location');
        const destDiv = document.getElementById('destination-location');
        const loader = document.getElementById('loader');
        const themeToggle = document.getElementById('theme-toggle');
        
        let map;
        let mapLayers = []; 
        let lightMapLayer, darkMapLayer;

        function initMap() {
            map = L.map('map', {zoomControl: false}).setView([12.87, 121.77], 6);

            lightMapLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
                maxZoom: 19
            });
            
            // --- *** THIS IS THE FIX: Use the reliable CartoDB dark map *** ---
            darkMapLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
                maxZoom: 19
            });

            // --- THIS IS THE FIX: Changed to bottomright ---
            L.control.zoom({
                position: 'bottomright'
            }).addTo(map);
            
            button.disabled = false;
            button.textContent = "Get Directions";
            
            originInput.addEventListener('blur', zoomToOrigin);
            themeToggle.addEventListener('change', toggleTheme);
            
            // Set initial theme
            const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (prefersDarkMode) {
                themeToggle.checked = true;
                document.body.classList.add('dark-mode');
                map.addLayer(darkMapLayer);
            } else {
                document.body.classList.remove('dark-mode');
                map.addLayer(lightMapLayer);
            }
        }
        
        function toggleTheme(e) {
            const isDarkMode = e.target.checked;
            document.body.classList.toggle('dark-mode', isDarkMode);
            
            if (isDarkMode) {
                if (map.hasLayer(lightMapLayer)) {
                    map.removeLayer(lightMapLayer);
                }
                map.addLayer(darkMapLayer);
            } else {
                if (map.hasLayer(darkMapLayer)) {
                    map.removeLayer(darkMapLayer);
                }
                map.addLayer(lightMapLayer);
            }
        }
        
        function clearMap() {
            mapLayers.forEach(layer => {
                if (map.hasLayer(layer)) {
                    map.removeLayer(layer);
                }
            });
            mapLayers = []; 

            stepsList.innerHTML = "";
            summaryText.innerHTML = "";
            summaryDiv.className = '';
            originDiv.innerHTML = "";
            destDiv.innerHTML = "";
            modeIcon.innerHTML = "";
        }

        function zoomToOrigin() {
            const place_name = originInput.value;
            if (!place_name) return; 
            
            window.pywebview.api.zoom_to_place(place_name).then(jsonData => {
                const data = JSON.parse(jsonData);
                if (data.status === 'success' && data.coords) {
                    map.flyTo(data.coords, 13);
                }
            });
        }

        function getIconForSign(sign) {
            switch(sign) {
                case -3: return '<span class="icon">↙️</span>';
                case -2: return '<span class="icon">⬅️</span>';
                case -1: return '<span class="icon">↖️</span>';
                case 0:  return '<span class="icon">⬆️</span>';
                case 1:  return '<span class="icon">↗️</span>';
                case 2:  return '<span class="icon">➡️</span>';
                case 3:  return '<span class="icon">↘️</span>';
                case 4:  return '<span class="icon">🏁</span>';
                case 5:  return '<span class="icon">📍</span>';
                case 6:  return '<span class="icon">🔄</span>';
                default: return '<span class="icon">·</span>';
            }
        }

        function handleApiResponse(data) {
            button.disabled = false;
            button.textContent = "Get Directions";
            loader.style.display = 'none';
            clearMap();

            if (data.error || data.status !== 'success') {
                summaryDiv.className = 'error';
                summaryText.innerHTML = data.error || "An unknown error occurred.";
                return;
            }

            try {
                const mode = modeSelect.value;
                let icon = '🚗';
                if (mode === 'Walking') icon = '🚶';
                if (mode === 'Bicycling') icon = '🚲';
                
                modeIcon.innerHTML = icon;
                originDiv.innerHTML = `<strong>From:</strong> ${data.origin_address}`;
                destDiv.innerHTML = `<strong>To:</strong> ${data.destination_address}`;

                summaryText.innerHTML = `
                    Est. Time: ${data.duration} <br>
                    Distance: ${data.distance}
                `;
                summaryDiv.className = '';
            } catch (e) {
                console.error("Error setting text:", e);
            }
            
            const startLatLng = data.origin_coords; 
            const endLatLng = data.destination_coords;
            
            try {
                const routeLine = L.polyline(data.polyline_coords, {
                    color: "var(--map-line)",
                    weight: 5,
                    opacity: 0.9,
                    renderer: L.svg({ padding: 1 }),
                    filter: 'drop-shadow(0 0 5px var(--map-glow))' 
                });
                
                routeLine.addTo(map);
                mapLayers.push(routeLine);
            } catch (e) {
                console.error("Failed to draw route line:", e);
            }
        
            try {
                const startMarker = L.marker(startLatLng).bindPopup(data.origin_address);
                const endMarker = L.marker(endLatLng).bindPopup(data.destination_address);
                
                startMarker.addTo(map);
                endMarker.addTo(map);
                
                mapLayers.push(startMarker);
                mapLayers.push(endMarker);
            } catch (e) {
                console.error("Failed to draw markers:", e);
            }
        
            try {
                const bounds = L.latLngBounds([startLatLng, endLatLng]);
                if (bounds.isValid()) {
                    map.fitBounds(bounds, { padding: [50, 50] });
                } else {
                    map.setView(startLatLng, 8);
                }
            } catch (e) {
                console.error("Failed to fit map bounds:", e);
            }
        
            try {
                data.steps.forEach(step => {
                    const li = document.createElement('li');
                    const icon = getIconForSign(step.sign);
                    li.innerHTML = `${icon} ${step.text}`;
                    stepsList.appendChild(li); 
                });
            } catch (e) {
                console.error("Failed to display directions:", e);
                stepsList.innerHTML = "<li>Error displaying directions.</li>";
            }
        }

        button.addEventListener('click', () => {
            const origin = originInput.value;
            const destination = destInput.value;
            const mode = modeSelect.value;

            if (!origin || !destination) {
                summaryDiv.className = 'error';
                summaryText.innerHTML = "Please enter both an origin and a destination.";
                return;
            }
            
            if (mode === 'Transit' || mode === 'Truck') {
                clearMap();
                summaryDiv.className = 'error';
                modeIcon.innerHTML = (mode === 'Transit') ? '🚌' : '🚚';
                summaryText.innerHTML = `"${mode}" is not supported by the free GraphHopper API.`;
                return;
            }

            button.disabled = true;
            loader.style.display = 'block';
            clearMap();

            window.pywebview.api.get_directions(origin, destination, mode)
                .then(jsonData => {
                    const data = JSON.parse(jsonData);
                    handleApiResponse(data);
                });
        });

        window.addEventListener('load', initMap);
    </script>
</body>
</html>
"""

# 3. THE PYTHON APP LAUNCHER
if __name__ == '__main__':
    api = Api()

    webview.create_window(
        'GraphHopper Land Route Directions',
        html=html_content,
        js_api=api,
        width=1200,
        height=800
    )
    
    webview.start()