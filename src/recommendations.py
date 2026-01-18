"""
Restaurant and activity recommendations using Google Places API
"""

import googlemaps
from typing import List, Dict, Optional
from src.distance_calculator import DistanceCalculator


class RecommendationEngine:
    """Generate restaurant and activity recommendations"""

    def __init__(self, api_key: str, distance_calculator: DistanceCalculator, config: Dict):
        """Initialize with Google Maps API key and configuration"""
        self.gmaps = googlemaps.Client(key=api_key)
        self.distance_calc = distance_calculator
        self.config = config

    def get_restaurant_recommendations(self, hotel_location: str) -> List[Dict]:
        """
        Get restaurant recommendations near hotel

        Args:
            hotel_location: Hotel address or coordinates

        Returns:
            List of restaurant recommendations
        """
        print(f"\n🍽️  Finding restaurants near hotel...")

        coords = self.distance_calc.get_coordinates(hotel_location)

        if not coords:
            print("   ❌ Could not find hotel location")
            return []

        restaurants = []

        # Search for halal restaurants
        if self.config['restaurant_preferences']['halal_only']:
            restaurants.extend(self._search_halal_restaurants(coords))

        # Search for upscale restaurants
        restaurants.extend(self._search_upscale_restaurants(coords))

        # Remove duplicates
        unique_restaurants = {}
        for restaurant in restaurants:
            place_id = restaurant.get('place_id')
            if place_id and place_id not in unique_restaurants:
                unique_restaurants[place_id] = restaurant

        # Get detailed information
        detailed_restaurants = []
        for restaurant in list(unique_restaurants.values())[:20]:  # Limit to 20
            details = self._get_restaurant_details(restaurant['place_id'])
            if details:
                # Calculate distance from hotel
                distance = self._calculate_distance_from_coords(coords, details['location'])
                details['distance_km'] = distance

                # Calculate score
                score = self._calculate_restaurant_score(details)
                details['score'] = score

                detailed_restaurants.append(details)

        # Filter by rating
        min_rating = self.config['restaurant_preferences']['min_rating']
        filtered = [r for r in detailed_restaurants if r['rating'] >= min_rating]

        # Sort by score
        filtered.sort(key=lambda x: x['score'], reverse=True)

        max_results = self.config['restaurant_preferences']['max_results']
        print(f"   Found {len(filtered)} restaurants")

        return filtered[:max_results]

    def get_activity_recommendations(self, hotel_location: str) -> List[Dict]:
        """
        Get activity recommendations near hotel

        Args:
            hotel_location: Hotel address or coordinates

        Returns:
            List of activity recommendations
        """
        print(f"\n🎭 Finding activities near hotel...")

        coords = self.distance_calc.get_coordinates(hotel_location)

        if not coords:
            print("   ❌ Could not find hotel location")
            return []

        activities = []
        max_distance = self.config['activity_preferences']['max_distance_from_hotel_km']

        # Search for different types of activities
        activity_types = [
            ('museum', 'Museums & Culture'),
            ('art_gallery', 'Art Galleries'),
            ('tourist_attraction', 'Tourist Attractions'),
            ('night_club', 'Nightlife'),
            ('bar', 'Bars & Lounges'),
            ('theater', 'Theater & Shows'),
            ('shopping_mall', 'Shopping'),
        ]

        for place_type, category in activity_types:
            results = self._search_activities(coords, place_type, max_distance)
            for result in results:
                result['category'] = category
                activities.append(result)

        # Remove duplicates
        unique_activities = {}
        for activity in activities:
            place_id = activity.get('place_id')
            if place_id and place_id not in unique_activities:
                unique_activities[place_id] = activity

        # Get detailed information
        detailed_activities = []
        for activity in list(unique_activities.values())[:30]:  # Limit to 30
            details = self._get_activity_details(activity['place_id'])
            if details:
                # Add category
                details['category'] = activity.get('category', 'Other')

                # Calculate distance from hotel
                distance = self._calculate_distance_from_coords(coords, details['location'])
                details['distance_km'] = distance

                # Calculate score
                score = self._calculate_activity_score(details)
                details['score'] = score

                detailed_activities.append(details)

        # Sort by score
        detailed_activities.sort(key=lambda x: x['score'], reverse=True)

        max_results = self.config['activity_preferences']['max_results']
        print(f"   Found {len(detailed_activities)} activities")

        return detailed_activities[:max_results]

    def _search_halal_restaurants(self, coords: Tuple[float, float]) -> List[Dict]:
        """Search for halal restaurants"""
        try:
            result = self.gmaps.places_nearby(
                location=coords,
                radius=5000,  # 5km
                keyword='halal restaurant',
                type='restaurant'
            )

            return result.get('results', [])

        except Exception as e:
            print(f"   Error searching halal restaurants: {e}")
            return []

    def _search_upscale_restaurants(self, coords: Tuple[float, float]) -> List[Dict]:
        """Search for upscale restaurants"""
        try:
            keywords = ['fine dining', 'upscale', 'contemporary', 'gourmet']
            all_results = []

            for keyword in keywords:
                result = self.gmaps.places_nearby(
                    location=coords,
                    radius=5000,  # 5km
                    keyword=keyword,
                    type='restaurant'
                )

                all_results.extend(result.get('results', []))

            return all_results

        except Exception as e:
            print(f"   Error searching upscale restaurants: {e}")
            return []

    def _search_activities(self, coords: Tuple[float, float], place_type: str, max_distance_km: int) -> List[Dict]:
        """Search for activities of a specific type"""
        try:
            result = self.gmaps.places_nearby(
                location=coords,
                radius=max_distance_km * 1000,
                type=place_type
            )

            return result.get('results', [])

        except Exception as e:
            print(f"   Error searching activities ({place_type}): {e}")
            return []

    def _get_restaurant_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a restaurant"""
        try:
            result = self.gmaps.place(
                place_id=place_id,
                fields=[
                    'name', 'rating', 'user_ratings_total', 'price_level',
                    'formatted_address', 'geometry', 'types', 'reviews',
                    'website', 'formatted_phone_number', 'opening_hours',
                    'editorial_summary'
                ]
            )

            if result.get('result'):
                place = result['result']

                return {
                    'place_id': place_id,
                    'name': place.get('name'),
                    'rating': place.get('rating', 0),
                    'num_reviews': place.get('user_ratings_total', 0),
                    'price_level': place.get('price_level', 0),
                    'address': place.get('formatted_address'),
                    'location': place.get('geometry', {}).get('location', {}),
                    'types': place.get('types', []),
                    'reviews': place.get('reviews', []),
                    'website': place.get('website'),
                    'phone': place.get('formatted_phone_number'),
                    'summary': place.get('editorial_summary', {}).get('overview'),
                    'is_open': place.get('opening_hours', {}).get('open_now', None)
                }

        except Exception as e:
            print(f"   Error getting restaurant details: {e}")

        return None

    def _get_activity_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for an activity"""
        try:
            result = self.gmaps.place(
                place_id=place_id,
                fields=[
                    'name', 'rating', 'user_ratings_total', 'price_level',
                    'formatted_address', 'geometry', 'types', 'reviews',
                    'website', 'formatted_phone_number', 'opening_hours',
                    'editorial_summary'
                ]
            )

            if result.get('result'):
                place = result['result']

                return {
                    'place_id': place_id,
                    'name': place.get('name'),
                    'rating': place.get('rating', 0),
                    'num_reviews': place.get('user_ratings_total', 0),
                    'price_level': place.get('price_level', 0),
                    'address': place.get('formatted_address'),
                    'location': place.get('geometry', {}).get('location', {}),
                    'types': place.get('types', []),
                    'reviews': place.get('reviews', []),
                    'website': place.get('website'),
                    'phone': place.get('formatted_phone_number'),
                    'summary': place.get('editorial_summary', {}).get('overview'),
                    'opening_hours': place.get('opening_hours', {})
                }

        except Exception as e:
            print(f"   Error getting activity details: {e}")

        return None

    def _calculate_distance_from_coords(
        self,
        coords1: Tuple[float, float],
        coords2: Dict
    ) -> float:
        """Calculate distance between two coordinate points"""
        from geopy.distance import geodesic

        if not coords2:
            return 999.0

        lat2 = coords2.get('lat')
        lng2 = coords2.get('lng')

        if lat2 is None or lng2 is None:
            return 999.0

        return geodesic(coords1, (lat2, lng2)).kilometers

    def _calculate_restaurant_score(self, restaurant: Dict) -> float:
        """
        Calculate restaurant score (0-100) based on preferences
        Higher score = better match
        """
        score = 50.0  # Base score

        # Rating scoring (up to +30 points)
        rating = restaurant['rating']
        score += (rating - 3.0) * 15

        # Number of reviews (up to +10 points)
        num_reviews = restaurant['num_reviews']
        if num_reviews > 500:
            score += 10
        elif num_reviews > 200:
            score += 7
        elif num_reviews > 100:
            score += 5

        # Price level (prefer upscale)
        price_level = restaurant.get('price_level', 0)
        if price_level >= 3:  # Upscale
            score += 15
        elif price_level == 2:  # Mid-range
            score += 8

        # Distance scoring
        distance = restaurant.get('distance_km', 999)
        if distance < 1:
            score += 15
        elif distance < 2:
            score += 10
        elif distance < 5:
            score += 5
        elif distance > 10:
            score -= 10

        # Halal bonus
        types = restaurant.get('types', [])
        if 'halal' in ' '.join(types).lower() or \
           'halal' in restaurant.get('name', '').lower():
            score += 20

        return max(score, 0)

    def _calculate_activity_score(self, activity: Dict) -> float:
        """
        Calculate activity score (0-100) based on preferences
        Higher score = better match
        """
        score = 50.0  # Base score

        # Rating scoring (up to +30 points)
        rating = activity['rating']
        if rating > 0:
            score += (rating - 3.0) * 15

        # Number of reviews (up to +10 points)
        num_reviews = activity['num_reviews']
        if num_reviews > 1000:
            score += 10
        elif num_reviews > 500:
            score += 7
        elif num_reviews > 100:
            score += 5

        # Distance scoring
        distance = activity.get('distance_km', 999)
        if distance < 1:
            score += 15
        elif distance < 2:
            score += 12
        elif distance < 3:
            score += 8
        elif distance < 5:
            score += 5
        elif distance > 8:
            score -= 5

        # Category-specific bonuses
        category = activity.get('category', '').lower()
        if 'museum' in category or 'culture' in category:
            score += 10
        elif 'nightlife' in category or 'bar' in category:
            score += 8

        return max(score, 0)

    def format_restaurant_results(self, restaurants: List[Dict]) -> str:
        """Format restaurant results for display"""
        if not restaurants:
            return "No restaurants found matching your criteria."

        output = ["\n" + "="*80]
        output.append("🍽️  RESTAURANT RECOMMENDATIONS")
        output.append("="*80 + "\n")

        for i, restaurant in enumerate(restaurants, 1):
            output.append(f"{i}. {restaurant['name']} - Score: {restaurant['score']:.0f}/100")
            output.append("-" * 80)

            # Rating and price
            if restaurant['rating'] > 0:
                output.append(f"Rating: {'⭐' * int(restaurant['rating'])} {restaurant['rating']}/5.0 ({restaurant['num_reviews']} reviews)")

            if restaurant.get('price_level'):
                price_symbols = '$' * restaurant['price_level']
                output.append(f"Price: {price_symbols}")

            # Distance
            if restaurant.get('distance_km') and restaurant['distance_km'] < 900:
                output.append(f"Distance from hotel: {restaurant['distance_km']:.1f}km")

            # Address and contact
            if restaurant.get('address'):
                output.append(f"Address: {restaurant['address']}")

            if restaurant.get('phone'):
                output.append(f"Phone: {restaurant['phone']}")

            if restaurant.get('website'):
                output.append(f"Website: {restaurant['website']}")

            # Summary
            if restaurant.get('summary'):
                output.append(f"About: {restaurant['summary']}")

            # Halal indicator
            if 'halal' in restaurant.get('name', '').lower() or \
               'halal' in ' '.join(restaurant.get('types', [])).lower():
                output.append("✓ Halal certified")

            # Sample review
            if restaurant.get('reviews') and len(restaurant['reviews']) > 0:
                review = restaurant['reviews'][0]
                rating = review.get('rating', 0)
                text = review.get('text', '')[:150]
                output.append(f"\n💭 Review: {'⭐' * rating}")
                output.append(f"   {text}...")

            output.append("")

        return "\n".join(output)

    def format_activity_results(self, activities: List[Dict]) -> str:
        """Format activity results for display"""
        if not activities:
            return "No activities found matching your criteria."

        output = ["\n" + "="*80]
        output.append("🎭 ACTIVITY RECOMMENDATIONS")
        output.append("="*80 + "\n")

        for i, activity in enumerate(activities, 1):
            output.append(f"{i}. {activity['name']} - Score: {activity['score']:.0f}/100")
            output.append("-" * 80)

            # Category
            output.append(f"Category: {activity.get('category', 'Other')}")

            # Rating
            if activity['rating'] > 0:
                output.append(f"Rating: {'⭐' * int(activity['rating'])} {activity['rating']}/5.0 ({activity['num_reviews']} reviews)")

            # Distance
            if activity.get('distance_km') and activity['distance_km'] < 900:
                output.append(f"Distance from hotel: {activity['distance_km']:.1f}km")

            # Address and contact
            if activity.get('address'):
                output.append(f"Address: {activity['address']}")

            if activity.get('website'):
                output.append(f"Website: {activity['website']}")

            # Opening hours
            if activity.get('opening_hours'):
                is_open = activity['opening_hours'].get('open_now')
                if is_open is not None:
                    status = "🟢 Open now" if is_open else "🔴 Closed now"
                    output.append(status)

            # Summary
            if activity.get('summary'):
                output.append(f"About: {activity['summary']}")

            output.append("")

        return "\n".join(output)
