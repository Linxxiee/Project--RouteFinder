import requests
import urllib.parse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# --- Initialize Rich Console ---
console = Console()

route_url = "https://graphhopper.com/api/1/route?"
# E261 Fix: Added two spaces before the inline comment
key = "27b08998-f69b-4d43-a3a6-3b4fda277646"  # Replace with your API key


# E302 Fix: Added two blank lines before function definition
def geocoding(location, key):
    """
    Translates a human-readable location string into geographic coordinates (lat, lng).
    Handles API calls, error checking, and formatting.
    """
    # W293 Fix: Removed trailing whitespace from blank lines inside functions
    
    # 1. Input Validation and URL Setup
    while location == "":
        location = console.input("[bold red]Location cannot be empty. Enter again: [/]")
    
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    params = {"q": location, "limit": "1", "key": key}
    url = geocode_url + urllib.parse.urlencode(params)

    try:
        # 2. API Call and Data Processing
        replydata = requests.get(url)
        json_status = replydata.status_code
        json_data = replydata.json()
        
        if json_status == 200 and len(json_data.get("hits", [])) != 0:
            # Success
            hit = json_data["hits"][0]
            lat = hit["point"]["lat"]
            lng = hit["point"]["lng"]
            name = hit.get("name", "N/A")
            value = hit.get("osm_value", "N/A")
            country = hit.get("country", "")
            state = hit.get("state", "")

            # Formatting the location name
            if name:
                new_loc = name
                # E701 Fix: Moved multiple statements onto separate lines
                if state:
                    new_loc += f", {state}"
                if country:
                    new_loc += f", {country}"
            else:
                new_loc = location
            
            console.print(f"[dim]Geocoding success for {new_loc} (Type: {value})[/dim]")
            return json_status, lat, lng, new_loc

        else:
            # API returned a status other than 200 or no hits
            lat = "null"
            lng = "null"
            new_loc = location
            msg = json_data.get('message', 'Unknown error')
            console.print(f"[bold red]Geocode API status: {json_status}\nError: {msg}[/]")
            return json_status, lat, lng, new_loc
            
    except requests.exceptions.RequestException as e:
        # Network or other request error
        console.print(f"[bold red]Network error during geocoding: {e}[/]")
        return "error", "null", "null", location


# E302 Fix: Added two blank lines before function definition
def _process_route_finder_logic(key, route_url):
    """
    Encapsulates the complex routing logic (user input, routing, and output)
    to satisfy the complexity check (C901).
    """
    profile = ["car", "bike", "foot"]
    
    # Vehicle Profile Input
    vehicle = console.input("[bold]Enter a vehicle profile: [/]").strip().lower()
    if vehicle == "quit" or vehicle == "q":
        return False
    elif vehicle not in profile:
        console.print("[yellow]No valid profile entered. Defaulting to 'car'[/]")
        vehicle = "car"
    
    # Starting Location Input and Geocoding
    loc1 = console.input("[bold]Starting Location: [/]").strip()
    if loc1 == "quit" or loc1 == "q":
        return False
    orig = geocoding(loc1, key)
    
    # Destination Input and Geocoding
    loc2 = console.input("[bold]Destination: [/]").strip()
    if loc2 == "quit" or loc2 == "q":
        return False
    dest = geocoding(loc2, key)
    
    console.print("=" * 50)
    
    # Route Finding Logic
    if orig[0] == 200 and dest[0] == 200:
        route_params = {
            "key": key, "vehicle": vehicle,
            "point": [f"{orig[1]},{orig[2]}", f"{dest[1]},{dest[2]}"],
            "instructions": True
        }
        paths_url = route_url + urllib.parse.urlencode(route_params, doseq=True)
        
        try:
            paths_response = requests.get(paths_url)
            paths_status = paths_response.status_code
            paths_data = paths_response.json()
            console.print(f"[dim]Routing API Status: {paths_status}[/]")
            
            if paths_status == 200 and paths_data.get("paths"):
                path_details = paths_data["paths"][0]
                
                # --- Calculate and Display Summary ---
                km = path_details["distance"] / 1000
                miles = km * 0.621371
                time_ms = path_details["time"]
                hr = int(time_ms / (1000 * 60 * 60))
                min_val = int((time_ms / (1000 * 60)) % 60)
                sec = int((time_ms / 1000) % 60)
                
                summary_text = Text()
                summary_text.append(f"From: {orig[3]}\n", style="bold green")
                summary_text.append(f"To:    {dest[3]}\n", style="bold red")
                summary_text.append(f"\nDistance: {miles:.1f} miles / {km:.1f} km\n", style="cyan")
                summary_text.append(f"Duration: {hr:02d}:{min_val:02d}:{sec:02d}", style="cyan")
                console.print(Panel(summary_text, title="Trip Summary", padding=1))
                
                # --- Create Directions Table ---
                table = Table(title="Turn-by-Turn Directions")
                table.add_column("Instruction", style="bold white", no_wrap=False, ratio=70)
                table.add_column("Distance (km)", style="magenta", ratio=15)
                table.add_column("Distance (mi)", style="magenta", ratio=15)
                
                for instruction in path_details["instructions"]:
                    path = instruction["text"]
                    dist_km = instruction["distance"] / 1000
                    dist_miles = dist_km * 0.621371
                    table.add_row(path, f"{dist_km:.2f}", f"{dist_miles:.2f}")
                console.print(table)
            else:
                msg = paths_data.get('message', 'Could not find a route')
                console.print(f"[bold red]Error: {msg}[/]")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Network error during routing: {e}[/]")
    else:
        console.print("[bold red]Could not get directions. Please check the locations entered.[/]")
    
    # E261 Fix: Added two spaces before the inline comment
    return True  # Continue the loop


# --- Main Application Loop (Simplified) ---
while True:
    console.print("\n" + "=" * 45)
    # E501 Fix: Wrapped the Panel.fit arguments to keep the line under 120 chars
    console.print(Panel.fit(
        "[bold cyan]Route Finder[/]\nAvailable profiles: [yellow]car, bike, foot[/]",
        title="Graphhopper",
        subtitle="Type 'q' to quit"
    ))
    
    if not _process_route_finder_logic(key, route_url):
        break

console.print("\n[bold cyan]Application terminated. Goodbye![/]\n")
