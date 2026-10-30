import os
import logging
import requests
from typing import Any
from dotenv import load_dotenv, find_dotenv, dotenv_values

types = ["restaurant", "cafe", "coffee_shop", "bakery", "fast_food_restaurant"]

def get_food_nearby_new_api(lat, lng, api_key, radius):
    url = "https://places.googleapis.com/v1/places:searchNearby"

    if not API_KEY:
        raise ValueError("PLACES_API_KEY not found in environment")

    headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.businessStatus,places.consumerAlert,places.attributions,places.websiteUri"
        }

    fetch_specification = {
        "includedTypes": types,
        "maxResultCount": 200,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius
            }
        }
    }

    try:
        response = requests.post(url, json=fetch_specification, headers=headers, timeout=10)
        response.raise_for_status()
        
        places_data = response.json().get('places', [])
        restaurants = []
        
        for place in places_data:
            restaurants.append({
                'name': place.get('displayName', {}).get('text', 'Unknown'),
                'place_id': place.get('id'),
                'address': place.get('formattedAddress', 'No address available'),
                'types': place.get('types', []),
                'business_status': place.get('businessStatus', 'Unknown'),
                'consumer_alert': place.get('consumerAlert', {}).get('text', 'No alert'),
                'website': place.get('websiteUri', 'No website available'),
                'attributions': place.get('attributions', [])
            })
            
        return restaurants
        
    except requests.exceptions.Timeout:
        logging.error("The request to the Google Places API timed out.")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"A network or HTTP error occurred: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred during data parsing: {e}")
        return []

if __name__ == "__main__":
    #load_dotenv(override=True)
    # 
    # 
    path = find_dotenv()
    print("Found .env at:", repr(path))        # empty string = file not found
    print("Loaded:", load_dotenv(path))        # False = nothing was loaded
    print("Keys in file:", list(dotenv_values(path).keys()))  # Load environment variables from .env file
    API_KEY = os.environ.get("PLACES_API_KEY")
    latitude = 49.260870231514225  
    longitude = -123.24484526733103  
    radius = 1000  # in meters

    nearby_restaurants = get_food_nearby_new_api(latitude, longitude, API_KEY, radius)
    for restaurant in nearby_restaurants:
        print(restaurant)
