"""
Hotel search module using Google Places API
"""

import googlemaps
from typing import List, Dict, Optional, Tuple
from src.distance_calculator import DistanceCalculator
from src.utils import format_distance, is_major_city


class HotelSearcher:
    """Search and filter hotels based on user preferences"""

    def __init__(self, api_key: str, distance_calculator: DistanceCalculator, config: Dict):
        """Initialize with Google Maps API key and configuration"""
        self.gmaps = googlemaps.Client(key=api_key)
        self.distance_calc = distance_calculator
        self.config = config

    def search_hotels(
        self,
        destination: str,
        customer_location: str,
        check_in_date: str,
        check_out_date: str,
        max_distance_km: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for hotels matching user preferences

        Args:
            destination: City or area to search for hotels
            customer_location: Where the customer is located (for distance calculation)
            check_in_date: Check-in date (YYYY-MM-DD)
            check_out_date: Check-out date (YYYY-MM-DD)
            max_distance_km: Maximum distance from customer (if None, will ask user)

        Returns:
            List of hotel options sorted by best match
        """
        print(f"\n🏨 Searching for hotels in {destination}...")

        # Determine search location
        search_location = self._determine_search_location(destination, customer_location)

        print(f"   Searching in: {search_location}")

        # Get distance to customer location
        distance_info = self.distance_calc.calculate_distance(search_location, customer_location)

        # Check if car rental is recommended
        if distance_info and distance_info['distance_km'] > self.config['hotel_preferences']['consider_car_rental_if_beyond_km']:
            print(f"   💡 Customer is {distance_info['distance_km']:.1f}km away - car rental recommended")

        # Search for hotels
        hotels = self._search_google_places_hotels(search_location)

        print(f"   Found {len(hotels)} hotels")

        # Filter by preferences
        filtered_hotels = self._filter_hotels(hotels, customer_location, search_location)

        print(f"   {len(filtered_hotels)} hotels match your preferences")

        # Sort by score
        filtered_hotels.sort(key=lambda x: x['score'], reverse=True)

        return filtered_hotels[:15]  # Return top 15 hotels

    def _determine_search_location(self, destination: str, customer_location: str) -> str:
        """
        Determine where to search for hotels
        If customer is in small town but destination is near a major city, might prefer the city
        """
        # Check if destination is a major city
        if is_major_city(destination):
            return destination

        # Calculate distance between destination and customer location
        distance_info = self.distance_calc.calculate_distance(destination, customer_location)

        if distance_info and distance_info['distance_km'] > 50:
            # Customer is far away - check if there's a major city nearby
            # For now, use the destination as-is
            # In a more advanced version, we could search for nearby major cities
            return destination

        return destination

    def _search_google_places_hotels(self, location: str) -> List[Dict]:
        """Search for hotels using Google Places API"""
        try:
            # Get coordinates for location
            coords = self.distance_calc.get_coordinates(location)

            if not coords:
                print(f"   ❌ Could not find coordinates for {location}")
                return []

            # Search for hotels
            # Use multiple searches to get better coverage
            all_hotels = []

            # Search 1: General hotel search
            result = self.gmaps.places_nearby(
                location=coords,
                radius=5000,  # 5km radius
                type='lodging',
                keyword='hotel'
            )

            all_hotels.extend(result.get('results', []))

            # Search 2: Specific hotel chains
            preferred_chains = self.config['hotel_preferences']['preferred_chains']
            for chain in preferred_chains[:3]:  # Search top 3 chains
                result = self.gmaps.places_nearby(
                    location=coords,
                    radius=10000,  # 10km radius for specific chains
                    keyword=chain
                )

                all_hotels.extend(result.get('results', []))

            # Remove duplicates
            unique_hotels = {}
            for hotel in all_hotels:
                hotel_id = hotel.get('place_id')
                if hotel_id and hotel_id not in unique_hotels:
                    unique_hotels[hotel_id] = hotel

            # Get detailed information for each hotel
            detailed_hotels = []
            for hotel in list(unique_hotels.values())[:30]:  # Limit to 30 to avoid API quota
                details = self._get_hotel_details(hotel['place_id'])
                if details:
                    detailed_hotels.append(details)

            return detailed_hotels

        except Exception as e:
            print(f"   Error searching hotels: {e}")
            return []

    def _get_hotel_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a hotel"""
        try:
            result = self.gmaps.place(
                place_id=place_id,
                fields=[
                    'name', 'rating', 'user_ratings_total', 'price_level',
                    'formatted_address', 'geometry', 'types', 'reviews',
                    'website', 'formatted_phone_number', 'opening_hours'
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
                    'is_open': place.get('opening_hours', {}).get('open_now', True)
                }

        except Exception as e:
            print(f"   Error getting hotel details: {e}")

        return None

    def _filter_hotels(self, hotels: List[Dict], customer_location: str, search_area: str) -> List[Dict]:
        """Filter hotels based on preferences and calculate scores"""
        filtered = []
        preferences = self.config['hotel_preferences']

        for hotel in hotels:
            # Check minimum rating
            if hotel['rating'] < preferences['min_rating']:
                continue

            # Check minimum number of reviews
            if hotel['num_reviews'] < preferences['min_reviews']:
                continue

            # Check for bad reviews
            if preferences['exclude_if_bad_reviews']:
                has_bad_reviews = self._has_bad_reviews(
                    hotel['reviews'],
                    preferences['bad_review_threshold']
                )
                if has_bad_reviews:
                    continue

            # Calculate distance from customer
            customer_distance = self._calculate_hotel_distance(hotel, customer_location)
            hotel['customer_distance_km'] = customer_distance

            # Check if within acceptable distance
            max_distance = preferences['max_uber_distance_km']
            if customer_distance and customer_distance > max_distance:
                # Only include if it's in a major city (user might prefer staying in the city)
                if not is_major_city(search_area):
                    continue

            # Calculate score
            score = self._calculate_hotel_score(hotel, customer_distance, search_area)

            if score > 0:
                hotel['score'] = score
                hotel['recommendation'] = self._get_hotel_recommendation(hotel, customer_distance, search_area)
                filtered.append(hotel)

        return filtered

    def _has_bad_reviews(self, reviews: List[Dict], threshold: float) -> bool:
        """Check if hotel has bad reviews"""
        if not reviews:
            return False

        # Count reviews below threshold
        bad_review_count = sum(1 for review in reviews if review.get('rating', 5) < threshold)

        # If more than 30% of reviews are bad, exclude
        if len(reviews) > 0 and (bad_review_count / len(reviews)) > 0.3:
            return True

        return False

    def _calculate_hotel_distance(self, hotel: Dict, customer_location: str) -> Optional[float]:
        """Calculate distance from hotel to customer location"""
        try:
            hotel_address = hotel['address']
            distance_info = self.distance_calc.calculate_distance(hotel_address, customer_location)

            if distance_info:
                return distance_info['distance_km']

        except Exception as e:
            print(f"   Error calculating distance for {hotel['name']}: {e}")

        return None

    def _calculate_hotel_score(self, hotel: Dict, customer_distance: Optional[float], search_area: str) -> float:
        """
        Calculate hotel score (0-100) based on preferences
        Higher score = better match
        """
        score = 50.0  # Base score

        # Rating scoring (up to +30 points)
        rating = hotel['rating']
        score += (rating - 3.0) * 15  # 4.0 rating = +15, 5.0 rating = +30

        # Number of reviews scoring (up to +10 points)
        num_reviews = hotel['num_reviews']
        if num_reviews > 500:
            score += 10
        elif num_reviews > 200:
            score += 7
        elif num_reviews > 100:
            score += 5

        # Preferred chain bonus (+15 points)
        hotel_name_lower = hotel['name'].lower()
        preferred_chains = [chain.lower() for chain in self.config['hotel_preferences']['preferred_chains']]

        for chain in preferred_chains:
            if chain in hotel_name_lower:
                score += 15
                break

        # Distance scoring
        if customer_distance:
            if customer_distance < 5:  # Very close
                score += 15
            elif customer_distance < 10:  # Close
                score += 10
            elif customer_distance < 20:  # Moderate
                score += 5
            elif customer_distance > 40:  # Far
                # Only acceptable if in major city
                if is_major_city(search_area):
                    score -= 5
                else:
                    score -= 20

        # Price level scoring (mid-range preferred for business travel)
        price_level = hotel.get('price_level', 0)
        if price_level == 3:  # Mid-high range (ideal for business)
            score += 10
        elif price_level == 4:  # Luxury
            score += 5
        elif price_level == 2:  # Mid range
            score += 8

        # Safety/area quality (based on rating - higher rated hotels usually in better areas)
        if rating >= 4.5:
            score += 10

        return max(score, 0)

    def _get_hotel_recommendation(self, hotel: Dict, customer_distance: Optional[float], search_area: str) -> str:
        """Get recommendation text for a hotel"""
        recommendations = []

        # Preferred chain
        hotel_name_lower = hotel['name'].lower()
        preferred_chains = [chain.lower() for chain in self.config['hotel_preferences']['preferred_chains']]

        for chain in preferred_chains:
            if chain in hotel_name_lower:
                recommendations.append(f"Preferred chain: {chain.title()}")
                break

        # Excellent rating
        if hotel['rating'] >= 4.5:
            recommendations.append("Excellent ratings")

        # Distance
        if customer_distance:
            if customer_distance < 5:
                recommendations.append("Very close to customer location")
            elif customer_distance < 10:
                recommendations.append("Close to customer location")
            elif customer_distance > 30 and is_major_city(search_area):
                recommendations.append("In major city - good for leisure")

        # High review count
        if hotel['num_reviews'] > 500:
            recommendations.append("Many verified reviews")

        return " • ".join(recommendations) if recommendations else "Good option"

    def get_car_rental_recommendation(self, destination: str, customer_location: str) -> Optional[Dict]:
        """Check if car rental is recommended"""
        distance_info = self.distance_calc.calculate_distance(destination, customer_location)

        if not distance_info:
            return None

        threshold = self.config['hotel_preferences']['consider_car_rental_if_beyond_km']

        if distance_info['distance_km'] > threshold:
            return {
                'recommended': True,
                'reason': f"Customer location is {distance_info['distance_km']:.1f}km away ({distance_info['duration_text']})",
                'distance_km': distance_info['distance_km'],
                'duration': distance_info['duration_text']
            }

        return {
            'recommended': False,
            'reason': f"Customer location is only {distance_info['distance_km']:.1f}km away - Uber is convenient",
            'distance_km': distance_info['distance_km'],
            'duration': distance_info['duration_text']
        }

    def format_hotel_results(self, hotels: List[Dict], car_rental_info: Optional[Dict] = None) -> str:
        """Format hotel results for display"""
        if not hotels:
            return "No hotels found matching your criteria."

        output = ["\n" + "="*80]
        output.append("🏨 HOTEL SEARCH RESULTS")
        output.append("="*80 + "\n")

        # Car rental recommendation
        if car_rental_info and car_rental_info['recommended']:
            output.append(f"🚗 CAR RENTAL RECOMMENDED")
            output.append(f"   {car_rental_info['reason']}")
            output.append("")

        for i, hotel in enumerate(hotels, 1):
            output.append(f"Option {i} - Score: {hotel['score']:.0f}/100")
            output.append("-" * 80)

            # Hotel details
            output.append(f"Hotel: {hotel['name']}")
            output.append(f"Rating: {'⭐' * int(hotel['rating'])} {hotel['rating']}/5.0 ({hotel['num_reviews']} reviews)")

            if hotel.get('price_level'):
                price_symbols = '$' * hotel['price_level']
                output.append(f"Price Level: {price_symbols}")

            output.append(f"Address: {hotel['address']}")

            # Distance
            if hotel.get('customer_distance_km'):
                output.append(f"Distance from customer: {hotel['customer_distance_km']:.1f}km")

            # Contact info
            if hotel.get('phone'):
                output.append(f"Phone: {hotel['phone']}")

            if hotel.get('website'):
                output.append(f"Website: {hotel['website']}")

            # Recommendations
            output.append(f"💡 {hotel['recommendation']}")

            # Sample reviews
            if hotel.get('reviews') and len(hotel['reviews']) > 0:
                output.append("\n📝 Recent reviews:")
                for review in hotel['reviews'][:2]:  # Show top 2 reviews
                    rating = review.get('rating', 0)
                    text = review.get('text', '')[:100]  # First 100 chars
                    output.append(f"   {'⭐' * rating} - {text}...")

            output.append("")

        return "\n".join(output)
