# Ibn Battuta - Automated Travel Booking System

Named after the famous medieval Muslim scholar and traveler Ibn Battuta, this system automates the tedious process of finding flights, hotels, and making travel plans for business trips.

## 🎯 Quick Links

- **[Web UI Guide](WEB_UI_README.md)** - Beautiful web interface setup
- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **CLI Usage** - See below

## Overview

This automated travel booking system helps busy professionals find the best travel options based on their specific preferences. Instead of manually searching multiple websites and comparing options, you provide your departure and destination, and the system does all the work for you.

**NEW!** 🎨 **Web Interface Available** - Use the beautiful React UI to search and view results. See [WEB_UI_README.md](WEB_UI_README.md)

### What It Does

1. **Flight Search**: Searches for flights across multiple airports and filters based on your preferences:
   - **✈️ Aeroplan Member Bonus**: Prioritizes Air Canada and Star Alliance partners so you keep collecting points
   - Prefers non-stop flights
   - Checks if airports are within your acceptable distance from home/destination
   - Automatically suggests business class upgrades when they're good value
   - Considers seat preferences (aisle, front of plane, away from washrooms)

2. **Hotel Search**: Finds the best hotels based on:
   - **💰 Budget Control**: Set your max budget per night ($100-$1000)
   - **☕ Area Intelligence**: Prioritizes areas with great coffee shops, historical vibes, or trendy/new neighborhoods
   - Preferred hotel chains (Holiday Inn, Hilton, Marriott, Citizen M, etc.)
   - Google reviews and ratings
   - Distance from customer location
   - Safe, nice areas (especially important in major cities)
   - Suggests car rental when customer is far from hotel

3. **Recommendations**: Provides curated lists of:
   - Halal, upscale restaurants near your hotel
   - Cultural attractions, museums, nightlife, and activities
   - All within walking distance or short Uber ride

## Features

- ✈️ **Smart Flight Search**: Uses Amadeus API with Aeroplan prioritization
- 🏨 **Hotel Intelligence**: Budget control + area preferences (coffee shops, historical, trendy)
- 🍽️ **Halal-Friendly**: Prioritizes halal restaurants and dining options
- 🗺️ **Distance-Aware**: Calculates distances and travel times using Google Maps
- 💼 **Business-Focused**: Optimized for business travelers with comfort and efficiency in mind
- 🎯 **Highly Customizable**: All preferences configurable via YAML file
- 🚀 **Fast**: Runs searches in parallel for quick results
- 📊 **Smart Scoring**: Ranks all options by how well they match your preferences
- 🎨 **Modern Web UI**: Beautiful React interface for easy searching and browsing

## Prerequisites

- Python 3.8 or higher
- Google Maps API key (for hotel search, restaurants, activities, and distances)
- Amadeus API credentials (for flight search)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ibn_battuta
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Keys

#### Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Places API
   - Distance Matrix API
   - Geocoding API
4. Create credentials (API key)
5. Copy your API key

#### Amadeus API Credentials

1. Go to [Amadeus for Developers](https://developers.amadeus.com/)
2. Create a free account
3. Create a new app
4. Copy your API Key and API Secret

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
```

### 5. Customize Your Preferences

Edit `config.yaml` to match your preferences:

```yaml
flight_preferences:
  seat_type: "aisle"
  prefer_nonstop: true
  max_distance_from_home_km: 100
  business_class_upgrade:
    enabled: true
    min_flight_duration_hours: 2
    max_price_difference_percent: 30

hotel_preferences:
  preferred_chains:
    - "Holiday Inn"
    - "Hilton"
    - "Marriott"
    - "Citizen M"
  min_rating: 4.0

restaurant_preferences:
  halal_only: true
  style:
    - "upscale"
    - "fine dining"
```

## Usage

### Interactive Mode

Run the system in interactive mode where it will ask you for trip details:

```bash
python main.py
```

You'll be prompted for:
- Departure city/airport
- Destination city/airport
- Customer location
- Travel dates
- Round trip or one-way

### Automated Mode

Provide all details via command line for fully automated operation:

```bash
# Round trip
python main.py --origin "Toronto" --destination "London" --customer "Central London" --departure 2024-03-15 --return 2024-03-20

# One-way trip
python main.py --origin YYZ --destination SFO --customer "San Francisco" --departure 2024-03-15

# Using airport codes
python main.py --origin JFK --destination LHR --customer "Canary Wharf" --departure 2024-04-01 --return 2024-04-05
```

### Example Output

```
================================================================================
✈️  FLIGHT SEARCH RESULTS
================================================================================

Option 1 - Score: 85/100
--------------------------------------------------------------------------------
Flight: AC850
Carrier: AC
Price: $650.00
Class: ECONOMY
Departure: 2024-03-15 10:30 from Toronto Pearson International Airport
Arrival: 2024-03-15 22:45 at London Heathrow Airport
Duration: 7h 15m
✓ Non-stop flight
💡 Non-stop • Convenient departure airport

Option 2 - Score: 92/100
--------------------------------------------------------------------------------
Flight: AC850
Carrier: AC
Price: $850.00
Class: BUSINESS
✨ Business class upgrade available! Only 30.8% more expensive ($200.00)
💡 Business class recommended for this duration
...

================================================================================
🏨 HOTEL SEARCH RESULTS
================================================================================

Option 1 - Score: 88/100
--------------------------------------------------------------------------------
Hotel: Hilton London Canary Wharf
Rating: ⭐⭐⭐⭐⭐ 4.5/5.0 (1247 reviews)
Price Level: $$$
Address: South Quay, Marsh Wall, London E14 9SH, UK
Distance from customer: 0.3km
💡 Preferred chain: Hilton • Excellent ratings • Very close to customer location

📝 Recent reviews:
   ⭐⭐⭐⭐⭐ - Great location for business travelers, walking distance to Canary Wharf...
   ⭐⭐⭐⭐⭐ - Excellent service and amenities. The executive lounge was fantastic...
...

================================================================================
🍽️  RESTAURANT RECOMMENDATIONS
================================================================================

1. Roka Canary Wharf - Score: 85/100
--------------------------------------------------------------------------------
Rating: ⭐⭐⭐⭐⭐ 4.6/5.0 (892 reviews)
Price: $$$$
Distance from hotel: 0.5km
Address: 4 Park Pavilion, 40 Canada Square, London E14 5FW
About: Contemporary Japanese robatayaki restaurant with sleek, stylish decor
💭 Review: ⭐⭐⭐⭐⭐
   Exceptional dining experience. The halal options are clearly marked and the...
```

## Configuration Options

### Flight Preferences

- `seat_type`: Preferred seat type (aisle, window, middle)
- `seat_location`: Preferred location (front, middle, back)
- `avoid_washrooms`: Avoid seats near washrooms
- `prefer_nonstop`: Prefer non-stop flights
- `max_distance_from_home_km`: Maximum acceptable distance from home to departure airport
- `max_distance_from_destination_km`: Maximum distance from destination to arrival airport
- `business_class_upgrade.enabled`: Enable automatic business class upgrade suggestions
- `business_class_upgrade.min_flight_duration_hours`: Minimum flight duration for upgrade
- `business_class_upgrade.max_price_difference_percent`: Maximum acceptable price increase for upgrade

### Hotel Preferences

- `preferred_chains`: List of preferred hotel chains (in priority order)
- `min_rating`: Minimum acceptable Google rating
- `min_reviews`: Minimum number of reviews required
- `exclude_if_bad_reviews`: Exclude hotels with bad reviews
- `bad_review_threshold`: Rating threshold for "bad" reviews
- `max_uber_distance_km`: Maximum acceptable distance from customer location
- `consider_car_rental_if_beyond_km`: Distance threshold for car rental suggestion

### Restaurant Preferences

- `halal_only`: Only show halal restaurants
- `style`: Preferred restaurant styles (upscale, fine dining, contemporary, etc.)
- `min_rating`: Minimum Google rating
- `max_results`: Maximum number of results to show

### Activity Preferences

- `categories`: Types of activities to recommend
- `max_distance_from_hotel_km`: Maximum distance from hotel
- `max_results`: Maximum number of results to show

## How It Works

### Scoring System

The system uses an intelligent scoring algorithm to rank all options:

**Flights** (0-100 score):
- +30 points for non-stop
- +15 points for business class (on long flights)
- +10 points for convenient airport locations
- +10 points for shorter flight duration
- Penalty for stops, long distances, etc.

**Hotels** (0-100 score):
- Up to +30 points for rating (4.5+ stars gets max points)
- +15 points for preferred chain
- +15 points for proximity to customer
- +10 points for high review count
- +10 points for mid-high price range (business appropriate)
- +10 points for safe area (high-rated area)

**Restaurants & Activities** (0-100 score):
- Up to +30 points for rating
- +20 points for halal certification
- +15 points for upscale/fine dining
- +15 points for proximity to hotel
- +10 points for cultural/museum activities

### Distance Calculations

The system uses Google Maps Distance Matrix API to calculate:
- Driving distance and time
- Public transit options when driving isn't available
- Walking distance for nearby locations

### Business Class Upgrade Logic

The system automatically identifies business class upgrade opportunities when:
1. Flight duration > 2 hours (configurable)
2. Business class price is ≤ 30% more than economy (configurable)
3. Same flight times and route

Example: If economy is $650 and business is $850 (30.8% more), you'll see:
```
✨ Business class upgrade available! Only 30.8% more expensive ($200.00)
```

### Car Rental Recommendations

The system suggests car rental when:
- Customer location is > 30km from hotel area (configurable)
- Useful for customers in industrial parks or suburban areas
- Considers both distance and duration

## Advanced Usage

### Custom Search Areas

When your customer is in a small town but there's a major city nearby, the system will ask if you want to stay in the city instead:

```
Customer location is: Small Industrial Park
Would you prefer to stay in a different area (e.g., major city nearby)? (y/n): y
Where would you like to search for hotels?: Munich
```

This is perfect when your customer is 1 hour outside Munich, but you'd rather stay in Munich for better restaurants, nightlife, and activities.

### Batch Processing

Create a script to process multiple trips:

```python
from main import TravelAutomation

automation = TravelAutomation()

trips = [
    ("Toronto", "London", "Canary Wharf", "2024-03-15", "2024-03-20"),
    ("New York", "Paris", "La Défense", "2024-04-01", "2024-04-05"),
]

for origin, dest, customer, dep, ret in trips:
    automation.run_automated(origin, dest, customer, dep, ret)
```

## Limitations & Notes

1. **API Quotas**: Be aware of API quotas:
   - Google Maps: 40,000 requests/month (free tier)
   - Amadeus: 1,000 API calls/month (free tier)

2. **Flight Seat Selection**: The system recommends flights based on your seat preferences, but actual seat selection must be done manually during booking.

3. **Booking**: This system finds and recommends options but doesn't make bookings. You'll need to book manually through airline/hotel websites.

4. **Real-time Prices**: Flight prices change frequently. Prices shown are current at search time but may change.

5. **Halal Restaurants**: The system searches for halal restaurants but you should verify halal certification directly with the restaurant.

## Troubleshooting

### "Missing required API keys"

Make sure you've created a `.env` file and added all required API keys. Copy from `.env.example` and fill in your keys.

### "No flights found"

- Try widening the date range
- Try nearby airports (e.g., if searching "Toronto", try "YYZ")
- Check if the route exists (some routes may not have non-stop flights)
- Verify your Amadeus API credentials are correct

### "No hotels found"

- Try widening the search area
- Lower the `min_rating` in config.yaml
- Check the destination spelling
- Verify your Google Maps API key has the Places API enabled

### "Rate limit exceeded"

You've hit API quotas. Either:
- Wait for the quota to reset (usually monthly)
- Reduce the number of searches
- Upgrade to a paid API plan

## Cost Estimates

### API Costs (Monthly)

Free tier is sufficient for personal use:

- **Google Maps APIs**: Free up to 40,000 requests/month
  - Typical usage: ~50 requests per trip search
  - Free tier allows: ~800 trip searches/month

- **Amadeus API**: Free up to 1,000 calls/month
  - Typical usage: ~10 calls per trip search
  - Free tier allows: ~100 trip searches/month

For heavy usage, consider paid tiers:
- Google Maps: $5-7 per 1,000 requests beyond free tier
- Amadeus: Contact for enterprise pricing

## Future Enhancements

Potential improvements:
- [ ] Integration with booking APIs for automatic booking
- [ ] Email/Slack notifications with trip summaries
- [ ] Calendar integration (add to Google Calendar)
- [ ] Price tracking and alerts
- [ ] Multi-city trip support
- [ ] Travel expense estimation
- [ ] Integration with corporate travel policies
- [ ] Mobile app

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please open an issue on GitHub.

## Acknowledgments

- Named after Ibn Battuta (1304-1368), one of history's greatest travelers
- Built with Amadeus for Developers API
- Powered by Google Maps Platform
- Uses data from Google Places for reviews and recommendations

---

Happy travels! ✈️🌍
