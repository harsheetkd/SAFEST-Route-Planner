import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from datetime import datetime
import json

class CrimeDataProcessor:
    def __init__(self, crime_data_path):
        self.geolocator = Nominatim(user_agent="route_planner")
        self.crime_data = None
        self.city_stats = {}
        self._load_crime_data(crime_data_path)
        
    def _load_crime_data(self, path):
        """Load and process crime data"""
        try:
            # Load crime data
            self.crime_data = pd.read_csv(path)
            
            # Calculate crime statistics for each city
            for _, row in self.crime_data.iterrows():
                city = row['Area']
                if city not in self.city_stats:
                    self.city_stats[city] = {
                        'total_crimes': 0,
                        'crime_types': {
                            'Murder': 0,
                            'Kidnapping': 0,
                            'Burglary': 0,
                            'Assault': 0,
                            'Theft': 0,
                            'Fraud': 0,
                            'Cyber Crime': 0,
                            'Drug Possession': 0
                        }
                    }
                
                crime_type = row['Crime Type']
                if crime_type in self.city_stats[city]['crime_types']:
                    self.city_stats[city]['crime_types'][crime_type] += 1
                    self.city_stats[city]['total_crimes'] += 1
            
            print(f"Loaded crime data for {len(self.city_stats)} cities")
            
        except Exception as e:
            print(f"Error loading crime data: {e}")
            self.crime_data = None
            
    def calculate_risk_score(self, crime_stats):
        """Calculate risk score based on crime statistics"""
        if not crime_stats or crime_stats['total_crimes'] == 0:
            return 50  # Default risk score
            
        # Crime weights (higher weight = more dangerous)
        weights = {
            'Murder': 10,
            'Kidnapping': 9,
            'Burglary': 8,
            'Assault': 7,
            'Theft': 6,
            'Fraud': 5,
            'Cyber Crime': 4,
            'Drug Possession': 3
        }
        
        # Calculate weighted crime score
        total_weight = sum(weights.values())
        weighted_score = 0
        
        for crime_type, count in crime_stats['crime_types'].items():
            if crime_type in weights:
                weighted_score += count * weights[crime_type]
        
        # Normalize to 0-100 scale
        max_possible_score = total_weight * crime_stats['total_crimes']
        if max_possible_score == 0:
            return 100  # No crimes reported
            
        risk_score = (weighted_score / max_possible_score) * 100
        return max(0, min(100, risk_score))
    
    def get_city_crime_rate(self, city):
        """Get crime rate and statistics for a specific city"""
        try:
            # Get city coordinates
            location = self.geolocator.geocode(f"{city}, Dehradun")
            if not location:
                return {
                    'risk_percentage': 50,
                    'coordinates': None,
                    'city': 'Unknown'
                }
                
            # Get crime statistics
            crime_stats = self.city_stats.get(city, {
                'total_crimes': 0,
                'crime_types': {
                    'Murder': 0,
                    'Kidnapping': 0,
                    'Burglary': 0,
                    'Assault': 0,
                    'Theft': 0,
                    'Fraud': 0,
                    'Cyber Crime': 0,
                    'Drug Possession': 0
                }
            })
            
            # Calculate risk score
            risk_score = self.calculate_risk_score(crime_stats)
            
            return {
                'risk_percentage': risk_score,
                'coordinates': [location.latitude, location.longitude],
                'city': city,
                'total_crimes': crime_stats['total_crimes'],
                'crime_types': crime_stats['crime_types']
            }
            
        except Exception as e:
            print(f"Error getting stats for {city}: {e}")
            return {
                'risk_percentage': 50,
                'coordinates': None,
                'city': 'Unknown'
            }
    
    def calculate_route_risk(self, route):
        """Calculate risk based on route coordinates"""
        try:
            if not route or 'features' not in route:
                return {
                    'risk_percentage': 50,
                    'city': 'Unknown'
                }
                
            # Get route coordinates
            coords = route['features'][0]['geometry']['coordinates'][0]
            
            # Get city name from coordinates
            location = self.geolocator.reverse(f"{coords[1]}, {coords[0]}")
            if not location:
                return {
                    'risk_percentage': 50,
                    'city': 'Unknown'
                }
                
            # Extract city name
            city = location.raw['address'].get('city', location.raw['address'].get('town', 'Unknown'))
            
            # Get crime statistics for the city
            city_data = self.get_city_crime_rate(city)
            if city_data:
                return {
                    'risk_percentage': city_data['risk_percentage'],
                    'city': city,
                    'coordinates': city_data['coordinates'],
                    'total_crimes': city_data['total_crimes'],
                    'crime_types': city_data['crime_types']
                }
            
            return {
                'risk_percentage': 50,
                'city': 'Unknown'
            }
            
        except Exception as e:
            print(f"Error calculating route risk: {e}")
            return {
                'risk_percentage': 50,
                'city': 'Unknown'
            }

# Initialize the processor with Dehradun crime data
data_processor = CrimeDataProcessor('dehradun_crime_synthetic_data.csv')