import requests
from math import radians, cos, sin, asin, sqrt
from django.conf import settings
from typing import Tuple, Optional

def get_coordinates_from_village(village_name, taluka=None, district=None, state="Maharashtra"):
    try:
        if village_name:
            # Build URL with separate parameters
            base_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'format': 'json',
                'limit': 1,
                'village': village_name,
                'addressdetails': 1  # This helps get more detailed address info
            }
            
            # Add optional parameters if provided
            if taluka:
                params['county'] = taluka  # Nominatim uses 'county' for sub-district level
            if district:
                params['state_district'] = district  # Or use 'district'
            if state:
                params['state'] = state
            
            params['country'] = 'India'
            
            headers = {'User-Agent': 'YourAppName/1.0'}  # Always include this!
            
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
        return None, None
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None, None
