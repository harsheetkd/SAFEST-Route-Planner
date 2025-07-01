import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

# Load environment variables
load_dotenv()

# API Keys
ORS_API_KEY: Optional[str] = os.getenv('ORS_API_KEY')
WEATHER_API_KEY: Optional[str] = os.getenv('WEATHER_API_KEY')

# Safety Settings
DEFAULT_SAFETY_THRESHOLD: int = int(os.getenv('DEFAULT_SAFETY_THRESHOLD', 70))
MIN_SAFETY_THRESHOLD: int = int(os.getenv('MIN_SAFETY_THRESHOLD', 30))
MAX_SAFETY_THRESHOLD: int = int(os.getenv('MAX_SAFETY_THRESHOLD', 100))

# Emergency Contacts
EMERGENCY_CONTACTS: Dict[str, str] = {
    "police": os.getenv('POLICE_NUMBER', "100"),
    "ambulance": os.getenv('AMBULANCE_NUMBER', "108"),
    "fire_station": os.getenv('FIRE_STATION_NUMBER', "101"),
    "nearest_hospital": ""  # Will be calculated dynamically
}

# Map Settings
MAP_DEFAULT_CENTER: List[float] = [
    float(os.getenv('DEFAULT_CENTER_LAT', 30.3165)),
    float(os.getenv('DEFAULT_CENTER_LON', 78.0322))
]
MAP_DEFAULT_ZOOM: int = int(os.getenv('DEFAULT_ZOOM_LEVEL', 12))
MAP_HEIGHT: str = os.getenv('MAP_HEIGHT', '800px')
MAP_WIDTH: str = os.getenv('MAP_WIDTH', '100%')
MAX_MAP_POINTS: int = int(os.getenv('MAX_MAP_POINTS', 2))

# Dehradun bounding box coordinates
DEHRADUN_BOUNDING_BOX: Dict[str, float] = {
    "min_lon": 77.95,
    "min_lat": 30.25,
    "max_lon": 78.15,
    "max_lat": 30.45
}

# Safety Score Weights
CRIME_WEIGHTS: Dict[str, int] = {
    "Murder": 10,
    "Kidnapping": 9,
    "Burglary": 8,
    "Assault": 7,
    "Theft": 6,
    "Fraud": 5,
    "Cyber Crime": 4,
    "Drug Possession": 3
}

# Route Settings
MAX_ROUTE_DISTANCE: float = float(os.getenv('MAX_ROUTE_DISTANCE', 50.0))  # kilometers

# Geocoding Settings
GEOCODER_USER_AGENT: str = os.getenv('GEOCODER_USER_AGENT', 'route_planner')
GEOCODER_TIMEOUT: int = int(os.getenv('GEOCODER_TIMEOUT', 10))

# Cache Settings
CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
CACHE_TIMEOUT: int = int(os.getenv('CACHE_TIMEOUT', 3600))  # seconds
CACHE_MAX_SIZE: int = int(os.getenv('CACHE_MAX_SIZE', 1000))

# Logging Settings
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE: str = os.getenv('LOG_FILE', 'route_planner.log')
# Safety Score Weights
SAFETY_SCORE_WEIGHTS = {
    "weather": 30,
    "crime": 40,
    "traffic": 30
}
