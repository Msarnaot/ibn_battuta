#!/usr/bin/env python3
"""
Flask API for Ibn Battuta Travel Automation
Serves the React frontend and handles search requests
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import traceback
import os

from src.utils import load_config, load_env_vars, validate_api_keys
from src.distance_calculator import DistanceCalculator
from src.flight_search import FlightSearcher
from src.hotel_search import HotelSearcher
from src.recommendations import RecommendationEngine

app = Flask(__name__, static_folder='frontend/build')
CORS(app)

# Initialize components
print("Initializing Ibn Battuta API...")
config = load_config()
env_vars = load_env_vars()

if not validate_api_keys(env_vars):
    print("ERROR: Missing required API keys. Please check your .env file.")
    exit(1)

distance_calc = DistanceCalculator(env_vars['google_maps_api_key'])

flight_searcher = FlightSearcher(
    env_vars['amadeus_api_key'],
    env_vars['amadeus_api_secret'],
    distance_calc,
    config
)

hotel_searcher = HotelSearcher(
    env_vars['google_maps_api_key'],
    distance_calc,
    config
)

recommendation_engine = RecommendationEngine(
    env_vars['google_maps_api_key'],
    distance_calc,
    config
)

print("✓ API initialized successfully")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Ibn Battuta API'})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        'flight_preferences': config.get('flight_preferences', {}),
        'hotel_preferences': config.get('hotel_preferences', {}),
        'restaurant_preferences': config.get('restaurant_preferences', {}),
        'activity_preferences': config.get('activity_preferences', {})
    })


@app.route('/api/search', methods=['POST'])
def search_travel():
    """
    Main search endpoint

    Request body:
    {
        "origin": "Toronto",
        "destination": "London",
        "customer_location": "Central London",
        "departure_date": "2024-03-15",
        "return_date": "2024-03-20" (optional),
        "budget_per_night": 300 (optional)
    }
    """
    try:
        data = request.json

        # Validate required fields
        required_fields = ['origin', 'destination', 'customer_location', 'departure_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        origin = data['origin']
        destination = data['destination']
        customer_location = data['customer_location']
        departure_date = data['departure_date']
        return_date = data.get('return_date')
        budget_per_night = data.get('budget_per_night')

        print(f"\n🔍 API Search Request:")
        print(f"   From: {origin} → {destination}")
        print(f"   Customer at: {customer_location}")
        print(f"   Dates: {departure_date} to {return_date or 'one-way'}")
        if budget_per_night:
            print(f"   Budget: ${budget_per_night}/night")

        # Search flights
        print("\n1. Searching flights...")
        flights = flight_searcher.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=1
        )

        # Check business class upgrades
        if flights:
            flights = flight_searcher.check_business_class_upgrade(flights)

        print(f"   Found {len(flights)} flights")

        # Search hotels
        print("\n2. Searching hotels...")
        check_in = departure_date
        check_out = return_date if return_date else \
            (datetime.strptime(departure_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d")

        hotels = hotel_searcher.search_hotels(
            destination=destination,
            customer_location=customer_location,
            check_in_date=check_in,
            check_out_date=check_out,
            budget_per_night=budget_per_night
        )

        print(f"   Found {len(hotels)} hotels")

        # Get car rental recommendation
        car_rental_info = hotel_searcher.get_car_rental_recommendation(
            destination,
            customer_location
        )

        # Get recommendations for top hotel
        restaurants = []
        activities = []

        if hotels and len(hotels) > 0:
            print("\n3. Getting recommendations...")
            top_hotel = hotels[0]

            restaurants = recommendation_engine.get_restaurant_recommendations(
                top_hotel['address']
            )
            print(f"   Found {len(restaurants)} restaurants")

            activities = recommendation_engine.get_activity_recommendations(
                top_hotel['address']
            )
            print(f"   Found {len(activities)} activities")

        # Prepare response
        response = {
            'success': True,
            'search_params': {
                'origin': origin,
                'destination': destination,
                'customer_location': customer_location,
                'departure_date': departure_date,
                'return_date': return_date,
                'budget_per_night': budget_per_night
            },
            'flights': flights[:10],  # Top 10 flights
            'hotels': hotels[:10],  # Top 10 hotels
            'restaurants': restaurants,
            'activities': activities,
            'car_rental': car_rental_info,
            'summary': {
                'total_flights': len(flights),
                'total_hotels': len(hotels),
                'total_restaurants': len(restaurants),
                'total_activities': len(activities)
            }
        }

        print("\n✓ Search complete!")

        return jsonify(response)

    except Exception as e:
        print(f"\n❌ Error during search: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/flights', methods=['POST'])
def search_flights():
    """Search only flights"""
    try:
        data = request.json

        flights = flight_searcher.search_flights(
            origin=data['origin'],
            destination=data['destination'],
            departure_date=data['departure_date'],
            return_date=data.get('return_date'),
            adults=data.get('adults', 1)
        )

        if flights:
            flights = flight_searcher.check_business_class_upgrade(flights)

        return jsonify({
            'success': True,
            'flights': flights[:10],
            'total': len(flights)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hotels', methods=['POST'])
def search_hotels():
    """Search only hotels"""
    try:
        data = request.json

        hotels = hotel_searcher.search_hotels(
            destination=data['destination'],
            customer_location=data['customer_location'],
            check_in_date=data['check_in_date'],
            check_out_date=data['check_out_date'],
            budget_per_night=data.get('budget_per_night')
        )

        car_rental = hotel_searcher.get_car_rental_recommendation(
            data['destination'],
            data['customer_location']
        )

        return jsonify({
            'success': True,
            'hotels': hotels[:10],
            'car_rental': car_rental,
            'total': len(hotels)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get restaurant and activity recommendations"""
    try:
        data = request.json
        location = data['location']

        restaurants = recommendation_engine.get_restaurant_recommendations(location)
        activities = recommendation_engine.get_activity_recommendations(location)

        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'activities': activities
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React app"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Ibn Battuta Travel Automation API")
    print("="*50)
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
