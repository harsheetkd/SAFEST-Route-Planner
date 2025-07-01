import os
import time
from typing import Optional, List

import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from requests.exceptions import ReadTimeout
from dotenv import load_dotenv

from src.config.config import INDIA_BOUNDING_BOX  

# Load environment variables from .env file
load_dotenv()


class GeocodingService:
    def __init__(self):
        user_agent = os.getenv('GEOCODER_USER_AGENT', 'route_planner')
        try:
            timeout = int(os.getenv('GEOCODER_TIMEOUT', 10))
        except ValueError:
            timeout = 10

        self.geolocator = Nominatim(user_agent=user_agent, timeout=timeout)
        self.retry_delay = 1 

    def geocode_location(self, location_str: str, max_retries: int = 3) -> Optional[List[float]]:
        """
        Geocode a location string to coordinates within Dehradun.
        """
        if not location_str:
            st.error("Location string cannot be empty")
            return None

        # Try variations to increase geocoding success rate
        variations = [
            f"{location_str}, Dehradun",
            f"{location_str} area, Dehradun",
            f"{location_str} neighborhood, Dehradun"
        ]

        for variation in variations:
            for attempt in range(max_retries):
                try:
                    location = self.geolocator.geocode(variation)

                    if location:
                        if (INDIA_BOUNDING_BOX["min_lon"] <= location.longitude <= INDIA_BOUNDING_BOX["max_lon"] and
                                INDIA_BOUNDING_BOX["min_lat"] <= location.latitude <= INDIA_BOUNDING_BOX["max_lat"]):
                            return [location.latitude, location.longitude]
                        else:
                            st.warning(f"Location '{location_str}' is outside Dehradun bounds.")
                            return None

                except (GeocoderTimedOut, ReadTimeout):
                    if attempt < max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))  # exponential backoff
                        continue
                    st.error(f"Geocoding timed out after {max_retries} attempts")
                    return None

                except GeocoderUnavailable:
                    st.error("Geocoding service is currently unavailable. Please try again later.")
                    return None

                except Exception as e:
                    st.error(f"Unexpected error during geocoding: {str(e)}")
                    return None

                time.sleep(self.retry_delay)

        st.warning(f"Could not geocode location: '{location_str}' after multiple attempts.")
        return None
