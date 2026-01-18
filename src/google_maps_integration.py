"""
Google Maps Saved Places Integration
Pull user's saved restaurants and coffee shops to inform hotel selection
"""

import googlemaps
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from geopy.distance import geodesic


class SavedPlacesAnalyzer:
    """Analyze user's saved places to suggest hotel areas"""

    def __init__(self, api_key: str):
        """Initialize with Google Maps API key"""
        self.gmaps = googlemaps.Client(key=api_key)

    def get_saved_places_from_list(self, list_url: str = None) -> List[Dict]:
        """
        Get saved places from a Google Maps list

        Note: This requires the user to share their Google Maps list publicly
        or provide authentication. For now, we'll use a manual import approach.

        Args:
            list_url: URL to a public Google Maps list

        Returns:
            List of saved places
        """
        # TODO: Implement OAuth flow for private lists
        # For now, users can export their saved places manually
        return []

    def import_saved_places(self, places_data: List[Dict]) -> List[Dict]:
        """
        Import manually exported saved places

        Args:
            places_data: List of places with format:
                [
                    {
                        "name": "Blue Bottle Coffee",
                        "address": "123 Main St, San Francisco, CA",
                        "type": "cafe",
                        "coordinates": {"lat": 37.7749, "lng": -122.4194}
                    },
                    ...
                ]

        Returns:
            Processed places with additional metadata
        """
        processed_places = []

        for place in places_data:
            processed = {
                'name': place.get('name'),
                'address': place.get('address'),
                'type': place.get('type'),
                'coordinates': place.get('coordinates'),
                'city': self._extract_city_from_address(place.get('address', '')),
                'category': self._categorize_place(place)
            }
            processed_places.append(processed)

        return processed_places

    def _extract_city_from_address(self, address: str) -> str:
        """Extract city name from address"""
        # Simple extraction - in production, use geocoding
        parts = address.split(',')
        if len(parts) >= 2:
            # Usually: "Street, City, State/Country"
            return parts[-2].strip()
        return ""

    def _categorize_place(self, place: Dict) -> str:
        """Categorize a place"""
        place_type = place.get('type', '').lower()
        name = place.get('name', '').lower()

        if 'cafe' in place_type or 'coffee' in name:
            return 'coffee'
        elif 'restaurant' in place_type or 'food' in place_type:
            return 'restaurant'
        elif 'bar' in place_type or 'night' in place_type:
            return 'nightlife'
        elif 'museum' in place_type or 'gallery' in place_type:
            return 'culture'
        else:
            return 'other'

    def analyze_clusters_in_city(
        self,
        saved_places: List[Dict],
        city: str,
        radius_km: float = 2.0
    ) -> List[Dict]:
        """
        Find clusters of user's saved places in a city

        Args:
            saved_places: User's saved places
            city: City to analyze
            radius_km: Clustering radius in kilometers

        Returns:
            List of clusters with centroids and density
            [
                {
                    'centroid': (lat, lng),
                    'radius_km': float,
                    'place_count': int,
                    'places': [place1, place2, ...],
                    'categories': {'coffee': 3, 'restaurant': 2},
                    'score': float
                },
                ...
            ]
        """
        # Filter places in this city
        city_places = [
            p for p in saved_places
            if p.get('city', '').lower() == city.lower() or
            city.lower() in p.get('address', '').lower()
        ]

        if not city_places:
            return []

        # Simple clustering - find areas with multiple saved places nearby
        clusters = []
        used_places = set()

        for i, place in enumerate(city_places):
            if i in used_places:
                continue

            coords = place.get('coordinates')
            if not coords:
                continue

            center = (coords['lat'], coords['lng'])

            # Find all places within radius
            nearby_places = []
            nearby_indices = set()

            for j, other_place in enumerate(city_places):
                if j in used_places:
                    continue

                other_coords = other_place.get('coordinates')
                if not other_coords:
                    continue

                other_center = (other_coords['lat'], other_coords['lng'])
                distance = geodesic(center, other_center).kilometers

                if distance <= radius_km:
                    nearby_places.append(other_place)
                    nearby_indices.add(j)

            # Only create cluster if multiple places
            if len(nearby_places) >= 2:
                # Calculate centroid
                avg_lat = sum(p['coordinates']['lat'] for p in nearby_places) / len(nearby_places)
                avg_lng = sum(p['coordinates']['lng'] for p in nearby_places) / len(nearby_places)

                # Count categories
                categories = defaultdict(int)
                for p in nearby_places:
                    categories[p['category']] += 1

                # Calculate score based on count and diversity
                diversity_bonus = len(categories) * 5
                score = len(nearby_places) * 10 + diversity_bonus

                clusters.append({
                    'centroid': (avg_lat, avg_lng),
                    'radius_km': radius_km,
                    'place_count': len(nearby_places),
                    'places': nearby_places,
                    'categories': dict(categories),
                    'score': score
                })

                used_places.update(nearby_indices)

        # Sort by score (most places + diversity)
        clusters.sort(key=lambda x: x['score'], reverse=True)

        return clusters

    def calculate_hotel_saved_places_score(
        self,
        hotel_location: Tuple[float, float],
        saved_places: List[Dict],
        max_distance_km: float = 2.0
    ) -> Dict:
        """
        Calculate how close a hotel is to user's saved places

        Args:
            hotel_location: (lat, lng) of hotel
            saved_places: User's saved places
            max_distance_km: Maximum distance to consider

        Returns:
            {
                'score': float (0-50),
                'nearby_count': int,
                'categories': {'coffee': 2, 'restaurant': 1},
                'closest_places': [place1, place2, ...]
            }
        """
        nearby_places = []
        categories = defaultdict(int)

        for place in saved_places:
            coords = place.get('coordinates')
            if not coords:
                continue

            place_location = (coords['lat'], coords['lng'])
            distance = geodesic(hotel_location, place_location).kilometers

            if distance <= max_distance_km:
                nearby_places.append({
                    'place': place,
                    'distance_km': distance
                })
                categories[place['category']] += 1

        # Sort by distance
        nearby_places.sort(key=lambda x: x['distance_km'])

        # Calculate score
        # Base: 10 points per saved place nearby (max 30)
        # Bonus: 5 points per category type (max 20)
        nearby_count = len(nearby_places)
        count_score = min(nearby_count * 10, 30)
        diversity_score = min(len(categories) * 5, 20)

        total_score = count_score + diversity_score

        return {
            'score': total_score,
            'nearby_count': nearby_count,
            'categories': dict(categories),
            'closest_places': [p['place'] for p in nearby_places[:5]]
        }

    def get_recommended_search_areas(
        self,
        saved_places: List[Dict],
        city: str
    ) -> List[str]:
        """
        Get recommended neighborhoods to search for hotels

        Args:
            saved_places: User's saved places
            city: City to search

        Returns:
            List of neighborhood/area names
        """
        clusters = self.analyze_clusters_in_city(saved_places, city)

        if not clusters:
            return []

        # Use geocoding to get neighborhood names
        recommended_areas = []

        for cluster in clusters[:3]:  # Top 3 clusters
            centroid = cluster['centroid']

            try:
                # Reverse geocode to get area name
                result = self.gmaps.reverse_geocode(centroid)

                if result:
                    # Extract neighborhood from address components
                    for component in result[0].get('address_components', []):
                        if 'neighborhood' in component.get('types', []):
                            area_name = component['long_name']
                            if area_name not in recommended_areas:
                                recommended_areas.append(area_name)
                            break

                        if 'sublocality' in component.get('types', []):
                            area_name = component['long_name']
                            if area_name not in recommended_areas:
                                recommended_areas.append(area_name)
                            break

            except Exception as e:
                print(f"Error reverse geocoding cluster: {e}")

        return recommended_areas

    def format_saved_places_insights(
        self,
        saved_places: List[Dict],
        city: str
    ) -> str:
        """Format insights about saved places in a city"""
        city_places = [
            p for p in saved_places
            if p.get('city', '').lower() == city.lower() or
            city.lower() in p.get('address', '').lower()
        ]

        if not city_places:
            return f"No saved places found in {city}"

        # Count by category
        categories = defaultdict(int)
        for place in city_places:
            categories[place['category']] += 1

        insights = [
            f"Found {len(city_places)} saved place(s) in {city}:",
        ]

        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            insights.append(f"  • {count} {category} spot(s)")

        # Get clusters
        clusters = self.analyze_clusters_in_city(saved_places, city)

        if clusters:
            insights.append(f"\nFound {len(clusters)} area(s) with multiple saved places:")
            for i, cluster in enumerate(clusters[:3], 1):
                cat_str = ', '.join([f"{count} {cat}" for cat, count in cluster['categories'].items()])
                insights.append(f"  {i}. Area with {cluster['place_count']} places ({cat_str})")

        return '\n'.join(insights)
