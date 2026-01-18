"""
Distance calculation and location utilities using Google Maps API
"""

import googlemaps
from typing import Dict, Tuple, Optional, List
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


class DistanceCalculator:
    """Calculate distances and travel times using Google Maps"""

    def __init__(self, api_key: str):
        """Initialize with Google Maps API key"""
        self.gmaps = googlemaps.Client(key=api_key)
        self.geocoder = Nominatim(user_agent="ibn_battuta")

    def get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude for a location"""
        try:
            result = self.geocoder.geocode(location)
            if result:
                return (result.latitude, result.longitude)
        except Exception as e:
            print(f"Error geocoding {location}: {e}")

        return None

    def calculate_distance(self, origin: str, destination: str) -> Optional[Dict]:
        """
        Calculate distance and duration between two locations

        Returns:
            {
                'distance_km': float,
                'distance_text': str,
                'duration_minutes': int,
                'duration_text': str,
                'mode': str  # driving, transit
            }
        """
        try:
            # Try driving distance first
            result = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode='driving',
                units='metric'
            )

            if result['rows'][0]['elements'][0]['status'] == 'OK':
                element = result['rows'][0]['elements'][0]

                return {
                    'distance_km': element['distance']['value'] / 1000,
                    'distance_text': element['distance']['text'],
                    'duration_minutes': element['duration']['value'] / 60,
                    'duration_text': element['duration']['text'],
                    'mode': 'driving'
                }

            # If driving fails, try transit
            result = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode='transit',
                units='metric'
            )

            if result['rows'][0]['elements'][0]['status'] == 'OK':
                element = result['rows'][0]['elements'][0]

                return {
                    'distance_km': element['distance']['value'] / 1000,
                    'distance_text': element['distance']['text'],
                    'duration_minutes': element['duration']['value'] / 60,
                    'duration_text': element['duration']['text'],
                    'mode': 'transit'
                }

        except Exception as e:
            print(f"Error calculating distance: {e}")

        return None

    def get_nearby_airports(self, location: str, radius_km: int = 100) -> List[Dict]:
        """
        Find airports near a location

        Returns list of:
            {
                'name': str,
                'code': str,
                'distance_km': float,
                'location': str
            }
        """
        try:
            coords = self.get_coordinates(location)
            if not coords:
                return []

            # Search for airports
            result = self.gmaps.places_nearby(
                location=coords,
                radius=radius_km * 1000,
                type='airport'
            )

            airports = []
            for place in result.get('results', []):
                airport_coords = (
                    place['geometry']['location']['lat'],
                    place['geometry']['location']['lng']
                )

                distance = geodesic(coords, airport_coords).kilometers

                airports.append({
                    'name': place['name'],
                    'code': self._extract_airport_code(place['name']),
                    'distance_km': distance,
                    'location': place['vicinity']
                })

            # Sort by distance
            airports.sort(key=lambda x: x['distance_km'])

            return airports

        except Exception as e:
            print(f"Error finding airports: {e}")
            return []

    def _extract_airport_code(self, airport_name: str) -> str:
        """Extract IATA code from airport name"""
        # This is a simple extraction - you might want to use a proper airport database
        if '(' in airport_name and ')' in airport_name:
            start = airport_name.index('(') + 1
            end = airport_name.index(')')
            code = airport_name[start:end]
            if len(code) == 3:
                return code

        return ""

    def is_location_safe(self, location: str, city: str) -> Dict:
        """
        Check if a location is in a safe area
        This is a simplified version - in production, you'd use crime data APIs

        Returns:
            {
                'is_safe': bool,
                'safety_score': float,  # 0-10
                'notes': str
            }
        """
        try:
            # Get place details
            result = self.gmaps.find_place(
                input=f"{location}, {city}",
                input_type='textquery',
                fields=['name', 'rating', 'user_ratings_total', 'formatted_address']
            )

            if result.get('candidates'):
                place = result['candidates'][0]
                rating = place.get('rating', 0)

                # Simple heuristic: higher rated areas are generally safer
                # In production, use actual crime statistics APIs
                safety_score = min(rating * 2, 10)
                is_safe = safety_score >= 7

                return {
                    'is_safe': is_safe,
                    'safety_score': safety_score,
                    'notes': f"Area rating: {rating}/5.0"
                }

        except Exception as e:
            print(f"Error checking location safety: {e}")

        return {
            'is_safe': True,
            'safety_score': 7.0,
            'notes': "Unable to verify safety - manual check recommended"
        }

    def get_transit_directions(self, origin: str, destination: str) -> Optional[Dict]:
        """Get public transit directions"""
        try:
            result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode='transit',
                departure_time=datetime.now()
            )

            if result:
                route = result[0]
                leg = route['legs'][0]

                return {
                    'duration': leg['duration']['text'],
                    'distance': leg['distance']['text'],
                    'steps': [step['html_instructions'] for step in leg['steps']],
                    'summary': route['summary']
                }

        except Exception as e:
            print(f"Error getting transit directions: {e}")

        return None
