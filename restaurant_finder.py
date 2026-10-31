import os
import logging
import requests
import datetime
import json
from math import cos, radians
from typing import Any
from dotenv import load_dotenv, find_dotenv, dotenv_values

types = ["restaurant", "cafe", "coffee_shop", "bakery", "fast_food_restaurant"]
MAX_PAGES = 10


def center_to_rectangle(lat, lng, radius):
    """Convert a center point and distance (meters) into the low/high rectangle Google requires."""
    dlat = (radius / 1000) / 111.32
    dlng = (radius / 1000) / (111.32 * cos(radians(lat)))
    return {
        "low":  {"latitude": lat - dlat, "longitude": lng - dlng},   # southwest corner
        "high": {"latitude": lat + dlat, "longitude": lng + dlng},   # northeast corner
    }

def get_food_nearby_new_api(lat, lng, api_key, radius):
    url = "https://places.googleapis.com/v1/places:searchText"
    CURRENT_PAGE = 1

    if not api_key:
        raise ValueError("PLACES_API_KEY not found in environment")

    headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.types,places.businessStatus,places.consumerAlert,places.attributions,places.websiteUri,nextPageToken"
        }

    try:
        restaurants = []
        seen_place_ids = set()

        for place_type in types:
            fetch_specification = {
                "textQuery": place_type.replace("_", " "),
                "pageSize": 20,
                "locationRestriction": {
                    "rectangle": center_to_rectangle(lat, lng, radius)
                }
            }

            while CURRENT_PAGE < MAX_PAGES:
                response = requests.post(url, json=fetch_specification, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                places_data = data.get('places', [])

                for place in places_data:
                    if place.get('id') not in seen_place_ids:
                        seen_place_ids.add(place.get('id'))

                    restaurants.append({
                        'name': place.get('displayName', {}).get('text', 'Unknown'),
                        'place_id': place.get('id'),
                        'types': place.get('types', []),
                        'business_status': place.get('businessStatus', 'Unknown'),
                        'consumer_alert': place.get('consumerAlert', {}).get('text', 'No alert'),
                        'website': place.get('websiteUri', 'No website available'),
                        'attributions': place.get('attributions', [])
                    })

                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break

                CURRENT_PAGE += 1
                fetch_specification["pageToken"] = next_page_token

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
    load_dotenv(find_dotenv())
    API_KEY = os.environ.get("PLACES_API_KEY")
    latitude = 49.260870231514225  
    longitude = -123.24484526733103  
    radius = 1000  # in meters (distance from center to each edge of the square)

    nearby_restaurants = get_food_nearby_new_api(latitude, longitude, API_KEY, radius)
    path = f"data/restaurants_{datetime.datetime.now()}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nearby_restaurants, f, indent=2, ensure_ascii=False)