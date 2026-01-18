# Quick Start Guide

Get up and running with Ibn Battuta in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Get Your API Keys

### Google Maps API (Required)

1. Visit: https://console.cloud.google.com/
2. Create a new project
3. Enable these APIs:
   - Maps JavaScript API
   - Places API
   - Distance Matrix API
   - Geocoding API
4. Create an API key

### Amadeus API (Required)

1. Visit: https://developers.amadeus.com/
2. Sign up for free
3. Create a new app
4. Get your API Key and API Secret

## 3. Configure

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

Your `.env` should look like:
```
GOOGLE_MAPS_API_KEY=AIzaSyD...your_key_here
AMADEUS_API_KEY=hJk9k3j...your_key_here
AMADEUS_API_SECRET=2kL9s...your_secret_here
```

## 4. Customize Your Preferences (Optional)

Edit `config.yaml` to match your travel preferences:

```yaml
flight_preferences:
  prefer_nonstop: true
  max_distance_from_home_km: 100

hotel_preferences:
  preferred_chains:
    - "Hilton"
    - "Marriott"
  min_rating: 4.0

restaurant_preferences:
  halal_only: true
```

## 5. Run!

### Interactive Mode (Recommended for first time)

```bash
python main.py
```

Follow the prompts to enter your trip details.

### Automated Mode

```bash
python main.py \
  --origin "Toronto" \
  --destination "London" \
  --customer "Central London" \
  --departure 2024-03-15 \
  --return 2024-03-20
```

## That's It!

The system will now:
1. Search for the best flights ✈️
2. Find hotels matching your preferences 🏨
3. Recommend halal restaurants 🍽️
4. Suggest activities and attractions 🎭

## Example Output

You'll see results like:

```
Option 1 - Score: 85/100
Flight: AC850
Price: $650.00
Departure: 2024-03-15 10:30
✓ Non-stop flight
💡 Non-stop • Convenient departure airport

Hotel: Hilton London Canary Wharf
Rating: ⭐⭐⭐⭐⭐ 4.5/5.0
Distance from customer: 0.3km
💡 Preferred chain: Hilton • Excellent ratings
```

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- See [example.py](example.py) for programmatic usage examples
- Open an issue on GitHub if you encounter problems

## Pro Tips

1. **Use airport codes** for faster results: `--origin YYZ --destination LHR`

2. **Major city customers**: If your customer is in a small town 1hr from a major city, choose to stay in the major city for better restaurants and activities

3. **Business class upgrades**: The system automatically finds good business class deals on flights > 2 hours

4. **Car rental**: Watch for car rental recommendations when your customer is far from the hotel

5. **Customize scoring**: Edit the scoring functions in the source code to match your exact preferences

Happy travels! 🌍
