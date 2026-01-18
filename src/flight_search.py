"""
Flight search module using Amadeus API
"""

from amadeus import Client, ResponseError
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from src.distance_calculator import DistanceCalculator
from src.utils import format_currency, format_duration, calculate_price_difference_percent


class FlightSearcher:
    """Search and filter flights based on user preferences"""

    def __init__(self, api_key: str, api_secret: str, distance_calculator: DistanceCalculator, config: Dict):
        """Initialize with Amadeus API credentials and configuration"""
        self.amadeus = Client(
            client_id=api_key,
            client_secret=api_secret
        )
        self.distance_calc = distance_calculator
        self.config = config

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1
    ) -> List[Dict]:
        """
        Search for flights matching user preferences

        Args:
            origin: Departure city or airport code
            destination: Arrival city or airport code
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date (YYYY-MM-DD) for round trip
            adults: Number of adult passengers

        Returns:
            List of flight options sorted by best match
        """
        print(f"\n🔍 Searching for flights from {origin} to {destination}...")

        # Get nearby airports for origin and destination
        origin_airports = self._get_relevant_airports(origin, is_origin=True)
        dest_airports = self._get_relevant_airports(destination, is_origin=False)

        if not origin_airports or not dest_airports:
            print("❌ Could not find suitable airports")
            return []

        print(f"   Found {len(origin_airports)} origin airport(s) and {len(dest_airports)} destination airport(s)")

        all_flights = []

        # Search flights between all airport combinations
        for origin_airport in origin_airports:
            for dest_airport in dest_airports:
                flights = self._search_amadeus_flights(
                    origin_airport['code'],
                    dest_airport['code'],
                    departure_date,
                    return_date,
                    adults
                )

                # Add airport info to each flight
                for flight in flights:
                    flight['origin_airport'] = origin_airport
                    flight['dest_airport'] = dest_airport

                all_flights.extend(flights)

        print(f"   Found {len(all_flights)} total flight options")

        # Filter and score flights
        filtered_flights = self._filter_flights(all_flights)

        print(f"   {len(filtered_flights)} flights match your preferences")

        # Sort by score (best flights first)
        filtered_flights.sort(key=lambda x: x['score'], reverse=True)

        return filtered_flights[:10]  # Return top 10 flights

    def _get_relevant_airports(self, location: str, is_origin: bool) -> List[Dict]:
        """Get airports near a location within configured distance"""
        max_distance = self.config['flight_preferences']['max_distance_from_home_km'] if is_origin \
            else self.config['flight_preferences']['max_distance_from_destination_km']

        # If location looks like an airport code (3 letters), use it directly
        if len(location) == 3 and location.isalpha():
            return [{
                'name': f'{location} Airport',
                'code': location.upper(),
                'distance_km': 0,
                'location': location
            }]

        # Otherwise, search for nearby airports
        airports = self.distance_calc.get_nearby_airports(location, radius_km=max_distance)

        # Filter by distance
        relevant_airports = [
            airport for airport in airports
            if airport['distance_km'] <= max_distance and airport['code']
        ]

        return relevant_airports

    def _search_amadeus_flights(
        self,
        origin_code: str,
        dest_code: str,
        departure_date: str,
        return_date: Optional[str],
        adults: int
    ) -> List[Dict]:
        """Search flights using Amadeus API"""
        try:
            search_params = {
                'originLocationCode': origin_code,
                'destinationLocationCode': dest_code,
                'departureDate': departure_date,
                'adults': adults,
                'max': 50,  # Get more results for better filtering
                'currencyCode': 'USD'
            }

            if return_date:
                search_params['returnDate'] = return_date

            # Prefer non-stop flights
            if self.config['flight_preferences']['prefer_nonstop']:
                search_params['nonStop'] = 'true'

            response = self.amadeus.shopping.flight_offers_search.get(**search_params)

            flights = []
            for offer in response.data:
                flight_info = self._parse_flight_offer(offer)
                if flight_info:
                    flights.append(flight_info)

            return flights

        except ResponseError as error:
            # If no non-stop flights, search with stops
            if 'nonStop' in search_params:
                print(f"   No non-stop flights found, searching with stops...")
                del search_params['nonStop']
                try:
                    response = self.amadeus.shopping.flight_offers_search.get(**search_params)
                    flights = []
                    for offer in response.data:
                        flight_info = self._parse_flight_offer(offer)
                        if flight_info:
                            flights.append(flight_info)
                    return flights
                except Exception as e:
                    print(f"   Error searching flights: {e}")
                    return []
            else:
                print(f"   Error searching flights: {error}")
                return []

    def _parse_flight_offer(self, offer: Dict) -> Optional[Dict]:
        """Parse Amadeus flight offer into simplified format"""
        try:
            # Get the first itinerary (outbound flight)
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']

            # Calculate total duration
            total_duration = itinerary.get('duration', 'PT0H')
            duration_minutes = self._parse_duration(total_duration)

            # Get price information
            price = float(offer['price']['total'])
            currency = offer['price']['currency']

            # Get cabin class
            cabin_class = segments[0]['cabin']

            # Check if non-stop
            is_nonstop = len(segments) == 1

            # Get flight numbers and carriers
            flight_numbers = [f"{seg['carrierCode']}{seg['number']}" for seg in segments]
            carriers = list(set([seg['carrierCode'] for seg in segments]))

            return {
                'id': offer['id'],
                'price': price,
                'currency': currency,
                'cabin_class': cabin_class,
                'is_nonstop': is_nonstop,
                'duration_minutes': duration_minutes,
                'departure_time': segments[0]['departure']['at'],
                'arrival_time': segments[-1]['arrival']['at'],
                'flight_numbers': flight_numbers,
                'carriers': carriers,
                'num_stops': len(segments) - 1,
                'segments': segments,
                'raw_offer': offer
            }

        except Exception as e:
            print(f"   Error parsing flight offer: {e}")
            return None

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to minutes (e.g., 'PT2H30M' -> 150)"""
        import re

        hours = 0
        minutes = 0

        # Extract hours
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))

        # Extract minutes
        min_match = re.search(r'(\d+)M', duration_str)
        if min_match:
            minutes = int(min_match.group(1))

        return hours * 60 + minutes

    def _filter_flights(self, flights: List[Dict]) -> List[Dict]:
        """Filter flights based on preferences and calculate scores"""
        filtered = []

        for flight in flights:
            # Calculate score based on preferences
            score = self._calculate_flight_score(flight)

            if score > 0:
                flight['score'] = score
                flight['recommendation'] = self._get_flight_recommendation(flight)
                filtered.append(flight)

        return filtered

    def _calculate_flight_score(self, flight: Dict) -> float:
        """
        Calculate flight score (0-100) based on preferences
        Higher score = better match
        """
        score = 50.0  # Base score

        # Aeroplan airline prioritization (+20 points for Star Alliance)
        if self.config['flight_preferences'].get('aeroplan_member', False):
            preferred_airlines = self.config['flight_preferences'].get('preferred_airlines', [])
            flight_carriers = flight.get('carriers', [])

            # Check if any carrier is in preferred list
            for carrier in flight_carriers:
                if carrier in preferred_airlines:
                    score += 20
                    flight['is_aeroplan_friendly'] = True
                    break

        # Prefer non-stop flights (+30 points)
        if flight['is_nonstop']:
            score += 30
        else:
            # Penalty for stops (-15 points per stop)
            score -= flight['num_stops'] * 15

        # Prefer shorter flights (+10 points for < 5 hours, scaling down)
        if flight['duration_minutes'] < 300:  # < 5 hours
            score += 10
        elif flight['duration_minutes'] > 720:  # > 12 hours
            score -= 5

        # Cabin class scoring
        if flight['cabin_class'] == 'BUSINESS':
            # Business class is good for long flights
            if flight['duration_minutes'] > 120:  # > 2 hours
                score += 15
        elif flight['cabin_class'] == 'FIRST':
            score += 20

        # Price scoring (relative - lower is better, but not the only factor)
        # This is relative and will be adjusted based on all options

        # Airport distance scoring (closer is better)
        origin_distance = flight.get('origin_airport', {}).get('distance_km', 0)
        dest_distance = flight.get('dest_airport', {}).get('distance_km', 0)

        if origin_distance < 30:
            score += 10
        elif origin_distance > 80:
            score -= 10

        if dest_distance < 30:
            score += 10
        elif dest_distance > 80:
            score -= 10

        return max(score, 0)

    def _get_flight_recommendation(self, flight: Dict) -> str:
        """Get recommendation text for a flight"""
        recommendations = []

        # Aeroplan bonus
        if flight.get('is_aeroplan_friendly'):
            recommendations.append("✈️ Aeroplan points eligible")

        if flight['is_nonstop']:
            recommendations.append("Non-stop")

        if flight['cabin_class'] == 'BUSINESS':
            if flight['duration_minutes'] > 120:
                recommendations.append("Business class recommended for this duration")

        if flight.get('origin_airport', {}).get('distance_km', 0) < 30:
            recommendations.append("Convenient departure airport")

        if flight.get('dest_airport', {}).get('distance_km', 0) < 30:
            recommendations.append("Convenient arrival airport")

        return " • ".join(recommendations) if recommendations else "Good option"

    def check_business_class_upgrade(self, flights: List[Dict]) -> List[Dict]:
        """
        Check if business class upgrade makes sense for any flights
        Returns list of flights where upgrade is recommended
        """
        upgrade_config = self.config['flight_preferences']['business_class_upgrade']

        if not upgrade_config['enabled']:
            return flights

        min_duration = upgrade_config['min_flight_duration_hours'] * 60
        max_price_diff = upgrade_config['max_price_difference_percent']

        # Group flights by route (same departure/arrival times roughly)
        route_groups = {}

        for flight in flights:
            route_key = f"{flight['departure_time'][:10]}_{flight['arrival_time'][:10]}"

            if route_key not in route_groups:
                route_groups[route_key] = []

            route_groups[route_key].append(flight)

        # Find upgrade opportunities
        for route_flights in route_groups.values():
            economy_flights = [f for f in route_flights if f['cabin_class'] == 'ECONOMY']
            business_flights = [f for f in route_flights if f['cabin_class'] == 'BUSINESS']

            if economy_flights and business_flights:
                cheapest_economy = min(economy_flights, key=lambda x: x['price'])
                cheapest_business = min(business_flights, key=lambda x: x['price'])

                # Check if flight is long enough
                if cheapest_economy['duration_minutes'] >= min_duration:
                    price_diff_percent = calculate_price_difference_percent(
                        cheapest_economy['price'],
                        cheapest_business['price']
                    )

                    if price_diff_percent <= max_price_diff:
                        cheapest_business['upgrade_recommendation'] = (
                            f"✨ Business class upgrade available! "
                            f"Only {price_diff_percent:.1f}% more expensive "
                            f"({format_currency(cheapest_business['price'] - cheapest_economy['price'])})"
                        )

        return flights

    def format_flight_results(self, flights: List[Dict]) -> str:
        """Format flight results for display"""
        if not flights:
            return "No flights found matching your criteria."

        output = ["\n" + "="*80]
        output.append("✈️  FLIGHT SEARCH RESULTS")
        output.append("="*80 + "\n")

        for i, flight in enumerate(flights, 1):
            output.append(f"Option {i} - Score: {flight['score']:.0f}/100")
            output.append("-" * 80)

            # Flight details
            output.append(f"Flight: {', '.join(flight['flight_numbers'])}")
            output.append(f"Carrier: {', '.join(flight['carriers'])}")
            output.append(f"Price: {format_currency(flight['price'], flight['currency'])}")
            output.append(f"Class: {flight['cabin_class']}")

            # Times
            dep_time = datetime.fromisoformat(flight['departure_time'].replace('Z', '+00:00'))
            arr_time = datetime.fromisoformat(flight['arrival_time'].replace('Z', '+00:00'))

            output.append(f"Departure: {dep_time.strftime('%Y-%m-%d %H:%M')} from {flight['origin_airport']['name']}")
            output.append(f"Arrival: {arr_time.strftime('%Y-%m-%d %H:%M')} at {flight['dest_airport']['name']}")
            output.append(f"Duration: {format_duration(flight['duration_minutes'])}")

            # Stops
            if flight['is_nonstop']:
                output.append("✓ Non-stop flight")
            else:
                output.append(f"⚠ {flight['num_stops']} stop(s)")

            # Airport distances
            if flight['origin_airport']['distance_km'] > 0:
                output.append(f"Origin airport: {flight['origin_airport']['distance_km']:.1f}km from departure location")

            if flight['dest_airport']['distance_km'] > 0:
                output.append(f"Destination airport: {flight['dest_airport']['distance_km']:.1f}km from arrival location")

            # Recommendations
            output.append(f"💡 {flight['recommendation']}")

            # Upgrade recommendation if available
            if 'upgrade_recommendation' in flight:
                output.append(f"{flight['upgrade_recommendation']}")

            output.append("")

        return "\n".join(output)
