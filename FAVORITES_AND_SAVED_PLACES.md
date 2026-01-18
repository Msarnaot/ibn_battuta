# Favorites & Saved Places - Advanced Features

Two powerful memory features that make Ibn Battuta learn your preferences!

## Feature 1: Favorite Hotels 🏨⭐

**Remember your best stays and always get them recommended first.**

### How It Works

When you find a hotel you love, click the heart icon (❤️) to add it to your favorites. Next time you search in that city, your favorite hotel will:
- **Always appear at the top** (+50 score bonus!)
- Be marked with "⭐️ YOUR FAVORITE!"
- Get prioritized over all other options

### Using Favorites

#### Web UI

1. Search for hotels in any city
2. Click the **heart icon** (♡) on any hotel card
3. The heart turns **red** (❤️) - hotel is now a favorite!
4. Click again to remove from favorites

#### CLI

```python
from src.favorites_manager import FavoritesManager

favorites = FavoritesManager()

# Add a favorite
favorites.add_hotel({
    'place_id': 'ChIJ...',
    'name': 'Hilton London Canary Wharf',
    'address': 'South Quay, London',
    'city': 'London',
    'rating': 4.5,
    'location': {'lat': 51.5033, 'lng': -0.0195},
    'notes': 'Great location, quiet rooms'
})

# View all favorites
all_favs = favorites.get_all_favorites()

# Get favorites in a city
london_favs = favorites.get_favorites_by_city('London')
```

#### API Endpoints

```bash
# Get all favorites
GET /api/favorites

# Add to favorites
POST /api/favorites
{
  "place_id": "ChIJ...",
  "name": "Hotel Name",
  "address": "123 Main St",
  "city": "London",
  "rating": 4.5,
  "location": {"lat": 51.5, "lng": -0.1}
}

# Remove from favorites
DELETE /api/favorites/{place_id}

# Update notes
PUT /api/favorites/{place_id}/notes
{
  "notes": "Great breakfast, ask for room 302"
}
```

### Data Storage

Favorites are stored in `data/favorites.json`:

```json
{
  "hotels": [
    {
      "place_id": "ChIJ...",
      "name": "Hilton London Canary Wharf",
      "address": "South Quay, London",
      "city": "London",
      "rating": 4.5,
      "location": {"lat": 51.5033, "lng": -0.0195},
      "added_date": "2024-01-18T10:30:00",
      "notes": "Great location, quiet rooms"
    }
  ],
  "last_updated": "2024-01-18T10:30:00"
}
```

### Scoring Impact

- **Favorite hotels**: +50 points (HUGE bonus)
- **Result**: Favorites always appear first in search results
- **Benefit**: Never lose track of hotels you love

---

## Feature 2: Google Maps Saved Places 📍☕

**Your favorite coffee shops, restaurants, and spots help find the best hotel areas!**

### How It Works

Ibn Battuta analyzes your saved places from Google Maps to find hotel areas near your favorite spots. Hotels close to multiple saved places get bonus points, ensuring you stay in neighborhoods you already love.

### Benefits

- Hotels near your favorite coffee shops get +50 points
- Areas with multiple saved places are prioritized
- Automatically stay in familiar neighborhoods
- Combine your tastes with business requirements

### Setup Methods

#### Method 1: Google Takeout Export (Recommended)

1. Go to [Google Takeout](https://takeout.google.com/)
2. **Deselect all**, then select only **"Maps (your places)"**
3. Click **"Next step"** → **"Create export"**
4. Download the ZIP file
5. Extract and find `Saved Places.json`
6. Convert it:

```bash
python tools/export_google_maps_saved_places.py "Saved Places.json"
```

This creates `data/saved_places.json` automatically!

#### Method 2: Manual Creation

Create `data/saved_places.json` with this format:

```json
[
  {
    "name": "Blue Bottle Coffee",
    "address": "66 Mint St, San Francisco, CA 94103",
    "type": "cafe",
    "coordinates": {"lat": 37.7825, "lng": -122.4080}
  },
  {
    "name": "Tartine Bakery",
    "address": "600 Guerrero St, San Francisco, CA 94110",
    "type": "cafe",
    "coordinates": {"lat": 37.7614, "lng": -122.4244}
  },
  {
    "name": "SFMOMA",
    "address": "151 3rd St, San Francisco, CA 94103",
    "type": "museum",
    "coordinates": {"lat": 37.7858, "lng": -122.4009}
  }
]
```

**Types you can use**: `cafe`, `restaurant`, `bar`, `museum`, `nightlife`, `culture`, `other`

#### Method 3: API Upload (Web UI)

```bash
POST /api/saved-places
{
  "places": [
    {
      "name": "Coffee Shop Name",
      "address": "123 Main St, City, State",
      "type": "cafe",
      "coordinates": {"lat": 37.7749, "lng": -122.4194}
    }
  ]
}
```

### How It Affects Hotel Search

#### Scoring Formula

Hotels are scored based on proximity to your saved places:

- **Within 2km of saved places**:
  - Base: +10 points per saved place (max +30)
  - Diversity bonus: +5 points per category type (max +20)
  - **Total possible**: +50 points

#### Example

You have 3 cafes, 2 restaurants, and 1 bar saved in Paris.

**Hotel A** (near Marais):
- 500m from 2 of your cafes
- 800m from 1 restaurant
- **Score bonus**: +30 (3 places) + +15 (3 categories) = **+45 points**
- **Recommendation**: "📍 Near 3 of your coffee, restaurant"

**Hotel B** (far from saved places):
- No saved places within 2km
- **Score bonus**: 0 points

**Result**: Hotel A ranks much higher!

### Real-World Example

```
You save in London:
- 5 specialty coffee shops in Shoreditch
- 3 restaurants in Borough Market
- 2 bars in Soho

Search results:
1. ⭐⭐⭐ Hotel in Shoreditch - Score: 95/100
   📍 Near 5 of your coffee, restaurant
   ☕ Great area (coffee + culture)

2. Hotel near City of London - Score: 65/100
   📍 Near 1 of your coffee

3. Hotel in Westminster - Score: 60/100
   (No saved places nearby)
```

The Shoreditch hotel wins because it's near your favorite spots!

### Clustering Intelligence

The system finds "clusters" of your saved places:

```python
# Example: San Francisco saved places
Cluster 1 (Mission District):
  - 4 cafes
  - 3 restaurants
  - Score: 55

Cluster 2 (Downtown):
  - 2 cafes
  - 1 museum
  - Score: 35
```

Hotels near Cluster 1 get higher bonuses.

### Viewing Your Saved Places

```bash
# Get all saved places
GET /api/saved-places

Response:
{
  "success": true,
  "saved_places": [...],
  "total": 15
}
```

---

## Combined Power 💪

When you use **both features together**:

### Scenario 1: Repeat Business Trip

```
City: London
Favorite Hotel: Hilton Canary Wharf (+50 points)
Saved Places: 3 coffee shops in Canary Wharf (+35 points)

Final Score: 50 + 35 + base (70) = 155/100
Result: ALWAYS top recommendation!
```

### Scenario 2: New City with Saved Places

```
City: Paris (first visit, no favorites)
Saved Places: 5 cafes in Marais (+45 points)

Hotels in Marais: Score 115/100
Hotels elsewhere: Score 70/100
Result: Stay near your favorite spots!
```

### Scenario 3: Favorite + Different Area

```
City: Paris
Favorite Hotel: Hotel in 7th arrondissement (+50)
Saved Places: Cafes in Marais (+45)

Option 1: Favorite hotel - Score: 120/100
Option 2: Marais hotel - Score: 115/100

Result: Favorite still wins, but it's close!
You can choose based on trip purpose.
```

---

## Tips & Best Practices

### For Favorites

1. **Add favorites immediately** after a good stay
2. **Add notes** to remember details:
   - "Room 302 has best view"
   - "Ask for late checkout"
   - "Great gym on 5th floor"
3. **Review periodically** - hotels change!
4. **Use for regular destinations** - airports you fly through often

### For Saved Places

1. **Quality over quantity**: Save places you truly love
2. **Be specific with coordinates**: Use exact location
3. **Update regularly**: Add new discoveries
4. **Cover multiple categories**: Coffee + restaurants + culture = better recommendations
5. **Think about neighborhoods**: Save multiple spots in areas you like

### Power User Workflow

1. **Before trip**: Check which city you're visiting
2. **Check Google Maps**: Do you have saved places there?
3. **If no**: Quickly add 3-5 spots you'd want to try (from blogs, friends, etc.)
4. **If yes**: Run search - hotels near saved places rank higher!
5. **After trip**: If hotel was great, add to favorites ❤️

---

## Privacy & Data

### What's Stored Locally

- **Favorites**: `data/favorites.json` (on your machine only)
- **Saved Places**: `data/saved_places.json` (on your machine only)
- **No cloud sync**: Your data stays private

### Sharing Across Devices

To use on multiple computers:

```bash
# Export from Computer 1
cp data/favorites.json ~/Dropbox/ibn_battuta_favorites.json
cp data/saved_places.json ~/Dropbox/ibn_battuta_saved_places.json

# Import on Computer 2
cp ~/Dropbox/ibn_battuta_favorites.json data/favorites.json
cp ~/Dropbox/ibn_battuta_saved_places.json data/saved_places.json
```

Or use the API:

```bash
# Export
GET /api/favorites > my_favorites.json

# Import
POST /api/favorites < my_favorites.json
```

---

## Troubleshooting

### "Favorite hotel not appearing"

- Check the city name matches exactly
- Verify `data/favorites.json` exists
- Restart the API server

### "Saved places not affecting results"

- Ensure `data/saved_places.json` exists
- Check coordinates are correct
- Saved places must be within 2km of hotel
- Restart the API server after adding places

### "Google Takeout export not working"

- Try the manual JSON format instead
- Use the example generator:
  ```bash
  python tools/export_google_maps_saved_places.py --example
  ```
- Edit the example file with your places

### "Can't add favorite in UI"

- Check browser console for errors
- Verify API is running (`http://localhost:5000/api/health`)
- Try adding via CLI or API directly

---

## Advanced: Programmatic Usage

### Auto-Add Favorites After Booking

```python
from src.favorites_manager import FavoritesManager

def after_booking_hook(hotel_data):
    favorites = FavoritesManager()

    favorites.add_hotel({
        **hotel_data,
        'notes': f'Booked on {datetime.now()}'
    })

    print(f"Added {hotel_data['name']} to favorites!")
```

### Bulk Import Saved Places

```python
from src.google_maps_integration import SavedPlacesAnalyzer
import json

analyzer = SavedPlacesAnalyzer(api_key)

# Read CSV of your places
places = []
with open('my_places.csv') as f:
    for row in csv.DictReader(f):
        places.append({
            'name': row['name'],
            'address': row['address'],
            'type': row['type'],
            'coordinates': {
                'lat': float(row['lat']),
                'lng': float(row['lng'])
            }
        })

# Save
with open('data/saved_places.json', 'w') as f:
    json.dump(places, f, indent=2)
```

---

## Examples

### Example 1: Consulting Frequent Flyer

```python
# Cities visited regularly
cities = ['London', 'Paris', 'Munich', 'Amsterdam']

# Add favorite hotel in each
for city in cities:
    favorites.add_hotel(my_usual_hotel[city])

# Now every search prioritizes your favorites!
```

### Example 2: Foodie Traveler

```json
// data/saved_places.json
[
  // 20 Michelin-starred restaurants
  // 15 specialty coffee shops
  // 10 wine bars
]

// Result: Hotels always near great food!
```

### Example 3: Digital Nomad

```bash
# Save co-working spaces as "saved places"
# Hotels near co-working get bonus points
# Always stay in productive areas!
```

---

**Remember**: These features get smarter the more you use them. The system learns your preferences and keeps getting better at finding perfect hotels! 🚀
