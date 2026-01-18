"""
Favorites Manager - Store and retrieve user's favorite hotels
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class FavoritesManager:
    """Manage user's favorite hotels"""

    def __init__(self, favorites_file: str = "data/favorites.json"):
        """Initialize favorites manager"""
        self.favorites_file = favorites_file
        self._ensure_data_dir()
        self.favorites = self._load_favorites()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.favorites_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load_favorites(self) -> Dict:
        """Load favorites from file"""
        if not os.path.exists(self.favorites_file):
            return {
                'hotels': [],
                'last_updated': None
            }

        try:
            with open(self.favorites_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading favorites: {e}")
            return {
                'hotels': [],
                'last_updated': None
            }

    def _save_favorites(self):
        """Save favorites to file"""
        try:
            self.favorites['last_updated'] = datetime.now().isoformat()
            with open(self.favorites_file, 'w') as f:
                json.dump(self.favorites, indent=2, fp=f)
        except Exception as e:
            print(f"Error saving favorites: {e}")

    def add_hotel(self, hotel_data: Dict) -> bool:
        """
        Add a hotel to favorites

        Args:
            hotel_data: Hotel information including:
                - place_id: Google Places ID
                - name: Hotel name
                - address: Hotel address
                - city: City name
                - rating: Hotel rating
                - location: {lat, lng}

        Returns:
            True if added successfully, False if already exists
        """
        place_id = hotel_data.get('place_id')

        # Check if already exists
        if any(h['place_id'] == place_id for h in self.favorites['hotels']):
            return False

        favorite = {
            'place_id': place_id,
            'name': hotel_data.get('name'),
            'address': hotel_data.get('address'),
            'city': hotel_data.get('city'),
            'rating': hotel_data.get('rating'),
            'location': hotel_data.get('location'),
            'added_date': datetime.now().isoformat(),
            'notes': hotel_data.get('notes', '')
        }

        self.favorites['hotels'].append(favorite)
        self._save_favorites()
        return True

    def remove_hotel(self, place_id: str) -> bool:
        """
        Remove a hotel from favorites

        Args:
            place_id: Google Places ID

        Returns:
            True if removed, False if not found
        """
        original_length = len(self.favorites['hotels'])
        self.favorites['hotels'] = [
            h for h in self.favorites['hotels']
            if h['place_id'] != place_id
        ]

        if len(self.favorites['hotels']) < original_length:
            self._save_favorites()
            return True

        return False

    def get_all_favorites(self) -> List[Dict]:
        """Get all favorite hotels"""
        return self.favorites['hotels']

    def get_favorites_by_city(self, city: str) -> List[Dict]:
        """
        Get favorite hotels in a specific city

        Args:
            city: City name (case-insensitive)

        Returns:
            List of favorite hotels in that city
        """
        city_lower = city.lower()
        return [
            h for h in self.favorites['hotels']
            if h.get('city', '').lower() == city_lower or
            city_lower in h.get('address', '').lower()
        ]

    def is_favorite(self, place_id: str) -> bool:
        """Check if a hotel is in favorites"""
        return any(h['place_id'] == place_id for h in self.favorites['hotels'])

    def get_favorite_count(self) -> int:
        """Get total number of favorite hotels"""
        return len(self.favorites['hotels'])

    def get_cities_with_favorites(self) -> List[str]:
        """Get list of cities that have favorite hotels"""
        cities = set()
        for hotel in self.favorites['hotels']:
            if hotel.get('city'):
                cities.add(hotel['city'])
        return sorted(list(cities))

    def update_hotel_notes(self, place_id: str, notes: str) -> bool:
        """
        Update notes for a favorite hotel

        Args:
            place_id: Google Places ID
            notes: Notes to add

        Returns:
            True if updated, False if not found
        """
        for hotel in self.favorites['hotels']:
            if hotel['place_id'] == place_id:
                hotel['notes'] = notes
                self._save_favorites()
                return True

        return False

    def export_favorites(self) -> str:
        """Export favorites as JSON string"""
        return json.dumps(self.favorites, indent=2)

    def import_favorites(self, json_data: str) -> bool:
        """
        Import favorites from JSON string

        Args:
            json_data: JSON string containing favorites

        Returns:
            True if successful
        """
        try:
            imported = json.loads(json_data)

            # Merge with existing favorites (avoid duplicates)
            existing_place_ids = {h['place_id'] for h in self.favorites['hotels']}

            for hotel in imported.get('hotels', []):
                if hotel['place_id'] not in existing_place_ids:
                    self.favorites['hotels'].append(hotel)
                    existing_place_ids.add(hotel['place_id'])

            self._save_favorites()
            return True

        except Exception as e:
            print(f"Error importing favorites: {e}")
            return False
