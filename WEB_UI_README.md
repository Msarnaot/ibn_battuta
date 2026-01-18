# Ibn Battuta Web UI

Beautiful, modern web interface for the Ibn Battuta travel automation system.

## Features

- 🎨 **Modern Material-UI Design**: Clean, professional interface
- 🔍 **Instant Search**: Search flights, hotels, and recommendations in one go
- 💰 **Budget Control**: Set your hotel budget with an easy slider
- ✈️ **Aeroplan Priority**: Automatically prioritizes Aeroplan-friendly airlines
- ☕ **Area Preferences**: Hotels in areas with great coffee shops, historical sites, and trendy neighborhoods
- 📱 **Responsive**: Works on desktop, tablet, and mobile

## Quick Start

### 1. Install Backend Dependencies

```bash
# Make sure you're in the project root
cd /path/to/ibn_battuta

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Make sure your `.env` file is set up with the required API keys:

```bash
# Copy example if you haven't already
cp .env.example .env

# Edit .env and add your keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
```

### 3. Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### 4. Run the Application

You have two options:

#### Option A: Development Mode (Recommended for Testing)

Run backend and frontend separately:

**Terminal 1 - Backend:**
```bash
# From project root
python api.py
```

**Terminal 2 - Frontend:**
```bash
# From frontend directory
cd frontend
npm start
```

The app will open at `http://localhost:3000` with hot reload enabled.

#### Option B: Production Mode

Build the React app and serve it with Flask:

```bash
# Build React app
cd frontend
npm run build

# Start Flask server (from project root)
cd ..
python api.py
```

Visit `http://localhost:5000`

## Using the Web UI

### Search Form

1. **Departure**: Enter your departure city or airport code (e.g., "Toronto" or "YYZ")
2. **Destination**: Enter destination city or airport code (e.g., "London" or "LHR")
3. **Customer Location**: Where you'll be visiting your customer (optional, defaults to destination)
4. **Dates**: Select departure and return dates
5. **Budget**: Set your hotel budget per night using the slider ($100-$1000)
6. Click **"Search Travel Options"**

### Viewing Results

Results are organized in 4 tabs:

#### ✈️ Flights Tab
- See top 10 flights sorted by score
- **Aeroplan-friendly flights** are marked with ✈️ icon
- Business class upgrades shown when good value
- Non-stop flights prioritized
- Shows flight numbers, times, duration, and prices

#### 🏨 Hotels Tab
- Top 10 hotels sorted by preferences
- **Budget indicator**: Shows if within/over budget
- **Area quality**: Coffee shops, historical areas, trendy neighborhoods
- Preferred chains highlighted
- Distance from customer location
- Ratings and reviews

#### 🍽️ Restaurants Tab
- Halal restaurants near your hotel
- Upscale, fine dining options
- Ratings and distance from hotel
- Price level indicators

#### 🎭 Activities Tab
- Museums, cultural attractions
- Nightlife and entertainment
- All within walking distance of hotel
- Categorized for easy browsing

### Tips for Best Results

1. **Use Airport Codes**: "YYZ" instead of "Toronto" gives faster, more accurate results
2. **Specify Customer Location**: If your customer is in a suburb, put the exact area
3. **Adjust Budget**: Higher budgets give you more options in prime locations
4. **Round Trip vs One-Way**: Toggle based on your needs

## What Makes It Smart?

### Aeroplan Prioritization
- Automatically detects Air Canada and Star Alliance flights
- Adds +20 points to scoring for Aeroplan partners
- Shows ✈️ icon on Aeroplan-friendly flights

### Hotel Area Intelligence
- Searches for specialty coffee shops within 500m
- Detects historical districts in address
- Finds trendy/arts areas nearby
- Adds up to +20 points for great areas

### Budget Control
- Estimates hotel prices from Google price_level
- Applies penalties for over-budget hotels
- Gives bonuses for within-budget options
- Configurable in real-time via slider

### Smart Scoring
Everything is scored 0-100 based on:
- **Flights**: Aeroplan (+20), Non-stop (+30), Airport proximity (+10)
- **Hotels**: Budget fit (+5), Area quality (+20), Preferred chain (+15), Great ratings (+30)
- **Restaurants**: Halal (+20), Upscale (+15), High ratings (+30)

## Customization

### Change Preferences

Edit `config.yaml` to customize:

```yaml
flight_preferences:
  aeroplan_member: true
  preferred_airlines:
    - "AC"  # Air Canada
    - "UA"  # United
    # ... add more

hotel_preferences:
  budget_per_night_usd: 300
  area_preferences:
    - "coffee shops"
    - "historical"
    - "trendy"
```

### Theme Customization

Edit `frontend/src/App.js` to change colors:

```javascript
const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',  // Change this
    },
    // ...
  }
});
```

## API Endpoints

The backend provides these endpoints:

- `GET /api/health` - Health check
- `GET /api/config` - Get current configuration
- `POST /api/search` - Full search (flights + hotels + recommendations)
- `POST /api/flights` - Search flights only
- `POST /api/hotels` - Search hotels only
- `POST /api/recommendations` - Get recommendations for a location

## Troubleshooting

### "Cannot find module" errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API returns 500 errors
- Check your `.env` file has valid API keys
- Verify API quotas haven't been exceeded
- Check backend terminal for error messages

### Frontend won't start
```bash
# Make sure you're using Node.js 16+
node --version

# If old version, update Node.js then:
cd frontend
npm install
npm start
```

### Search takes too long
- This is normal! Flight and hotel searches can take 30-60 seconds
- The system searches multiple airports and hotel options
- Wait for the loading spinner to complete

### No results found
- Try broader search terms (city names instead of specific areas)
- Check dates are in the future
- Verify spelling of cities/airports
- Some routes may not have flights

## Performance Tips

- **First search is slowest**: API caches some data
- **Airport codes are faster**: "YYZ" vs "Toronto"
- **Free tier limits**: 100 searches/month (Amadeus), 800 searches/month (Google Maps)
- **Parallel requests**: Only run one search at a time to avoid rate limits

## Tech Stack

**Backend:**
- Flask (Python web framework)
- Amadeus API (flight search)
- Google Maps API (hotels, restaurants, activities, distances)

**Frontend:**
- React 18
- Material-UI (components)
- Axios (HTTP client)

## Next Steps

Want to enhance the UI? Ideas:
- Add flight seat selection preferences
- Save favorite searches
- Export results to PDF
- Email results
- Calendar integration
- Price tracking and alerts

## Support

Issues? Check:
1. Backend terminal for Python errors
2. Frontend console (F12) for JavaScript errors
3. API health: `curl http://localhost:5000/api/health`

---

**Enjoy your automated travel planning!** ✈️🌍
