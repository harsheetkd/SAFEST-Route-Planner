import folium
from folium import plugins
import streamlit as st
from streamlit_folium import st_folium
from src.config.config import MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM, MAP_HEIGHT, MAP_WIDTH

def create_map():
    """Create and return a new map instance"""
    return folium.Map(
        location=MAP_DEFAULT_CENTER,
        zoom_start=MAP_DEFAULT_ZOOM,
        tiles='OpenStreetMap',
        control_scale=True,
        prefer_canvas=True
    )

def add_click_handler(map):
    """Add click handler to map for selecting points"""
    map.get_root().html.add_child(folium.Element("""
        <script>
        var map = {{ this.get_name() }};
        var clickedPoints = [];
        
        map.on('click', function(e) {
            var latlng = e.latlng;
            
            // Add marker
            var marker = L.marker([latlng.lat, latlng.lng], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                })
            }).addTo(map);
            
            // Store coordinates
            clickedPoints.push([latlng.lat, latlng.lng]);
            
            // Update session state
            var sessionState = window.parent.document.querySelector('iframe').contentWindow.document;
            var sessionStateInput = sessionState.querySelector('input[name="clicked_points"]');
            if (sessionStateInput) {
                sessionStateInput.value = JSON.stringify(clickedPoints);
                sessionStateInput.dispatchEvent(new Event('input'));
            }
            
            // Remove marker if more than 2 points
            if (clickedPoints.length > 2) {
                map.removeLayer(marker);
                clickedPoints.pop();
                alert('Please select exactly two points: one for Start and one for End');
            }
        });
        </script>
        """))

def add_map_controls(map):
    """Add useful map controls"""
    folium.LayerControl().add_to(map)
    folium.LatLngPopup().add_to(map)
    plugins.Fullscreen().add_to(map)

def display_map(map):
    """Display the map in Streamlit"""
    return st_folium(
        map,
        height=MAP_HEIGHT,
        width=MAP_WIDTH,
        returned_objects=[]
    )
