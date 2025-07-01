import streamlit as st
import openrouteservice
import folium
from streamlit_folium import st_folium
import os
import math
from collections import defaultdict, deque
import heapq
import pandas as pd
import numpy as np
from datetime import datetime
from geopy.geocoders import Nominatim
import geopy.distance
from src.config.config import (
    ORS_API_KEY,
    DEFAULT_SAFETY_THRESHOLD,
    EMERGENCY_CONTACTS,
    MAP_DEFAULT_CENTER,
    DEHRADUN_BOUNDING_BOX,
    CRIME_WEIGHTS
)

# Initialize OpenRouteService client
client = openrouteservice.Client(key=ORS_API_KEY)

# Initialize geolocator
geolocator = Nominatim(user_agent="route_planner")

# Load crime data
crime_data = pd.read_csv('dehradun_crime_synthetic_data.csv')

# Cache for geocoding results
geocoding_cache = {}

# Function to validate coordinates
def validate_coordinates(coords):
    if not coords:
        return False
    lat, lon = coords
    bbox = DEHRADUN_BOUNDING_BOX
    return (bbox['min_lon'] <= lon <= bbox['max_lon'] and
            bbox['min_lat'] <= lat <= bbox['max_lat'])

# Function to geocode location (single definition)
def geocode_location(location):
    # Always bias to Dehradun
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="route_planner")
    query = f"{location}, Dehradun, Uttarakhand, India"
    loc = geolocator.geocode(query)
    if loc:
        return [loc.latitude, loc.longitude]
    return None

# Function to get area from coordinates
def get_area_from_coordinates(coords):
    try:
        cache_key = f"{coords[0]}_{coords[1]}"
        if cache_key in geocoding_cache:
            return geocoding_cache[cache_key]
        location = geolocator.reverse(f"{coords[1]}, {coords[0]}")
        if not location:
            return "Unknown Area"
        address = location.raw.get('address', {})
        area = address.get('suburb', address.get('neighbourhood', "Unknown Area"))
        geocoding_cache[cache_key] = area
        if len(geocoding_cache) > 1000:
            geocoding_cache.pop(next(iter(geocoding_cache)))
        return area
    except Exception as e:
        st.error(f"Error getting area: {e}")
        return "Unknown Area"

# Calculate safety scores based on crime data
def calculate_safety_score(location):
    try:
        area_crimes = crime_data[crime_data['Location'] == location]
        crime_weights = CRIME_WEIGHTS
        total_score = 0
        for _, crime in area_crimes.iterrows():
            crime_type = crime['Crime_Type']
            total_score += crime_weights.get(crime_type, 1)
        max_possible_score = sum(crime_weights.values()) * len(area_crimes)
        if max_possible_score == 0:
            return 100
        safety_score = (1 - (total_score / max_possible_score)) * 100
        return max(0, min(100, safety_score))
    except Exception as e:
        print(f"Error calculating safety score: {e}")
        return 0

# Graph representation of Dehradun roads
class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.weights = {}
        self.safety_scores = {}
    def add_edge(self, u, v, weight, safety_score):
        self.graph[u].append(v)
        self.graph[v].append(u)
        self.weights[(u, v)] = weight
        self.weights[(v, u)] = weight
        self.safety_scores[(u, v)] = safety_score
        self.safety_scores[(v, u)] = safety_score
    def get_neighbors(self, node):
        return self.graph[node]
    def get_weight(self, u, v):
        return self.weights.get((u, v), float('inf'))
    def get_safety_score(self, u, v):
        return self.safety_scores.get((u, v), 0)

# Dijkstra's algorithm with safety score consideration
def dijkstra(graph, start, end, safety_threshold=50):
    distances = {node: float('inf') for node in graph.graph}
    distances[start] = 0
    pq = [(0, start, [])]
    visited = set()
    while pq:
        (dist, current, path) = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        path = path + [current]
        if current == end:
            return path, dist
        for neighbor in graph.get_neighbors(current):
            if neighbor in visited:
                continue
            weight = graph.get_weight(current, neighbor)
            safety_score = graph.get_safety_score(current, neighbor)
            if safety_score < safety_threshold:
                continue
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor, path))
    return None, float('inf')

# A* algorithm with safety score consideration
def a_star(graph, start, end, safety_threshold=50):
    def heuristic(a, b):
        lat1, lon1 = a
        lat2, lon2 = b
        R = 6371
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a_ = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a_), math.sqrt(1-a_))
        return R * c
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in graph.graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph.graph}
    f_score[start] = heuristic(start, end)
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], g_score[end]
        for neighbor in graph.get_neighbors(current):
            tentative_g_score = g_score[current] + graph.get_weight(current, neighbor)
            if tentative_g_score >= g_score[neighbor]:
                continue
            safety_score = graph.get_safety_score(current, neighbor)
            if safety_score < safety_threshold:
                continue
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
            if neighbor not in [x[1] for x in open_set]:
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None, float('inf')

# Initialize graph with actual road network data
graph = Graph()
areas = crime_data['Location'].unique()
for area in areas:
    location = geolocator.geocode(f"{area}, Dehradun", timeout=10)
    if location:
        coords = (location.latitude, location.longitude)
        for other_area in areas:
            if other_area != area:
                other_location = geolocator.geocode(f"{other_area}, Dehradun", timeout=10)
                if other_location:
                    other_coords = (other_location.latitude, other_location.longitude)
                    distance = geopy.distance.geodesic(coords, other_coords).km
                    safety_score = calculate_safety_score(area)
                    graph.add_edge(
                        coords,
                        other_coords,
                        weight=distance,
                        safety_score=safety_score
                    )
graph.add_edge((30.3165, 78.0322), (30.3265, 78.0422), 2.5, 85)
graph.add_edge((30.3265, 78.0422), (30.3365, 78.0522), 3.0, 90)
graph.add_edge((30.3165, 78.0322), (30.3365, 78.0522), 4.0, 75)

# Dehradun coordinates and bounding box
dehradun_center = [30.3165, 78.0322]

# === Page configuration ===
st.set_page_config(page_title="Dehradun Route Planner", layout="wide")
st.title("Dehradun Route Planner 🚚")
st.markdown("""
Plan your routes within Dehradun city with ease!

1. Enter your pickup and delivery locations
2. View the route on the map
3. Check traffic conditions
4. Get safety recommendations
""")

default_safety_threshold = int(os.getenv('DEFAULT_SAFETY_THRESHOLD', 70))

def find_nearest_node(graph, coord):
    """Find the nearest node in the graph to the given coordinate (lat, lng)."""
    from math import radians, cos, sin, sqrt, atan2
    min_dist = float('inf')
    nearest = None
    lat1, lng1 = coord
    for node in graph.graph.keys():
        lat2, lng2 = node
        # Haversine formula
        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        dist = 6371 * c  # Earth radius in km
        if dist < min_dist:
            min_dist = dist
            nearest = node
    return nearest

def main():
    if 'clicked_points' not in st.session_state:
        st.session_state.clicked_points = []
    if 'find_routes' not in st.session_state:
        st.session_state.find_routes = False
    if 'map' not in st.session_state:
        st.session_state.map = folium.Map(
            location=dehradun_center,
            zoom_start=12,
            tiles='OpenStreetMap',
            control_scale=True,
            prefer_canvas=True
        )
        folium.LayerControl().add_to(st.session_state.map)
        folium.LatLngPopup().add_to(st.session_state.map)

    # === Safety Settings ===
    with st.sidebar:
        st.header("Safety Settings")
        safety_threshold = st.slider(
            "Minimum Safety Score",
            0,
            100,
            default_safety_threshold,
        )
        st.write(f"Routes below {safety_threshold}% safety score will be highlighted")
        max_route_distance = st.slider(
            "Maximum Route Distance (km)",
            1,
            100,
            int(os.getenv('MAX_ROUTE_DISTANCE', 50)),
            key="distance_threshold_slider"
        )
        st.write(f"Routes longer than {max_route_distance}km will be highlighted")
        st.header("Emergency Contacts")
        emergency_contacts = {
            "police": os.getenv('POLICE_NUMBER', "100"),
            "ambulance": os.getenv('AMBULANCE_NUMBER', "108"),
            "fire_station": os.getenv('FIRE_STATION_NUMBER', "101"),
        }
        for service, number in emergency_contacts.items():
            st.write(f"{service.capitalize()}: {number}")
        if 'saved_locations' not in st.session_state:
            st.session_state.saved_locations = []
        col1, col2 = st.columns(2)
        with col1:
            start_location = st.selectbox(
                "Start Location",
                options=["Enter new location"] + st.session_state.saved_locations,
                index=0,
                key="start_location_dropdown"
            )
            if start_location == "Enter new location":
                start_location_input = st.text_input(
                    "Enter Start Location",
                    key="start_location_input"
                )
            else:
                start_location_input = start_location
            if start_location_input and start_location_input != "Enter new location":
                if start_location_input not in st.session_state.saved_locations:
                    st.session_state.saved_locations.append(start_location_input)
                    st.session_state.saved_locations = st.session_state.saved_locations[-10:]
        with col2:
            end_location = st.selectbox(
                "End Location",
                options=["Enter new location"] + st.session_state.saved_locations,
                index=0,
                key="end_location_dropdown"
            )
            if end_location == "Enter new location":
                end_location_input = st.text_input(
                    "Enter End Location",
                    key="end_location_input"
                )
            else:
                end_location_input = end_location
            if end_location_input and end_location_input != "Enter new location":
                if end_location_input not in st.session_state.saved_locations:
                    st.session_state.saved_locations.append(end_location_input)
                    st.session_state.saved_locations = st.session_state.saved_locations[-10:]
        if st.session_state.saved_locations:
            st.write("Saved Locations:")
            for loc in st.session_state.saved_locations:
                st.write(f"- {loc}")

    st.write("""
    1. Enter start and end locations in Dehradun OR
    2. Click on the map to select start and end points
    3. The route will be automatically calculated
    """)

    start_location_input = st.text_input("Start Location", "")
    end_location_input = st.text_input("End Location", "")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Find Routes"):
            st.session_state.find_routes = True
    with col2:
        if st.button("Clear Markers and Inputs"):
            st.session_state.clicked_points = []
            st.session_state.map = folium.Map(
                location=dehradun_center,
                zoom_start=12,
                tiles='OpenStreetMap',
                control_scale=True,
                prefer_canvas=True
            )
            folium.LayerControl().add_to(st.session_state.map)
            folium.LatLngPopup().add_to(st.session_state.map)
            st.session_state.find_routes = False

    if st.session_state.get('find_routes', False) and (start_location_input and end_location_input):
        start_coords = geocode_location(start_location_input)
        end_coords = geocode_location(end_location_input)
        print(f"DEBUG: Start coords: {start_coords}, End coords: {end_coords}")
        # Snap to nearest graph node
        snapped_start = find_nearest_node(graph, tuple(start_coords))
        snapped_end = find_nearest_node(graph, tuple(end_coords))
        print(f"DEBUG: Snapped start: {snapped_start}, Snapped end: {snapped_end}")
        print(f"DEBUG: Start in graph: {snapped_start in graph.graph}")
        print(f"DEBUG: End in graph: {snapped_end in graph.graph}")
        if not snapped_start or not snapped_end:
            st.error("Could not find a nearby node in the graph for start or end location.")
            return
        folium.Marker(
            location=start_coords,
            popup=f"Start: {start_location_input}",
            icon=folium.Icon(color='green')
        ).add_to(st.session_state.map)
        folium.Marker(
            location=end_coords,
            popup=f"End: {end_location_input}",
            icon=folium.Icon(color='red')
        ).add_to(st.session_state.map)
        try:
            start_point = tuple(snapped_start)
            end_point = tuple(snapped_end)
            dijkstra_path, dijkstra_dist = dijkstra(graph, start_point, end_point, safety_threshold)
            a_star_path, a_star_dist = a_star(graph, start_point, end_point, safety_threshold)
            print(f"DEBUG: Dijkstra path: {dijkstra_path}")
            print(f"DEBUG: A* path: {a_star_path}")
            routes = []
            if dijkstra_path:
                dijkstra_coords = [[point[1], point[0]] for point in dijkstra_path]
                routes.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': dijkstra_coords
                    },
                    'properties': {
                        'name': 'Dijkstra Route',
                        'distance': dijkstra_dist,
                        'color': 'blue'
                    }
                })
            if a_star_path:
                a_star_coords = [[point[1], point[0]] for point in a_star_path]
                routes.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': a_star_coords
                    },
                    'properties': {
                        'name': 'A* Route',
                        'distance': a_star_dist,
                        'color': 'green'
                    }
                })
            for route in routes:
                folium.GeoJson(
                    route,
                    name=route['properties']['name'],
                    style_function=lambda x, color=route['properties']['color']: {
                        'color': color,
                        'weight': 5,
                        'opacity': 0.7
                    }
                ).add_to(st.session_state.map)
            st.subheader("Route Information")
            if dijkstra_path:
                st.write(f"Dijkstra Route Distance: {dijkstra_dist:.2f} km")
            if a_star_path:
                st.write(f"A* Route Distance: {a_star_dist:.2f} km")
            st.write("Blue line shows the Dijkstra route")
            st.write("Green line shows the A* route")
            st.write("Routes are calculated based on safety scores and distances")
            st.session_state.find_routes = False
            # After adding the routes, fit the map to the route bounds if a path exists and has more than 1 point
            if dijkstra_path and len(dijkstra_path) > 1:
                lats = [p[0] for p in dijkstra_path]
                lngs = [p[1] for p in dijkstra_path]
                bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]
                st.session_state.map.fit_bounds(bounds)
        except Exception as e:
            st.error(f"Error calculating route: {e}")
            st.session_state.find_routes = False
            return

    # Handle clicked points route
    if len(st.session_state.clicked_points) == 2:
        start_coords = [st.session_state.clicked_points[0]['lat'], st.session_state.clicked_points[0]['lng']]
        end_coords = [st.session_state.clicked_points[1]['lat'], st.session_state.clicked_points[1]['lng']]
        route = client.directions(
            coordinates=[start_coords[::-1], end_coords[::-1]],
            profile='driving-car',
            format='geojson'
        )
        folium.GeoJson(
            route,
            name='route',
            style_function=lambda x: {
                'color': 'blue',
                'weight': 5,
                'opacity': 0.7
            }
        ).add_to(st.session_state.map)
        st.subheader("Route Information")
        st.write("Route calculated successfully!")
        st.write("Blue line shows the driving route")

    # Always display the map at the end with increased size
    st_folium(st.session_state.map, height=700, width=1000, returned_objects=[])

if __name__ == "__main__":
    main()