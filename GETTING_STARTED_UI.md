# Getting Started - UI Only (No CLI Required!)

Everything you need through the web interface. No command-line tools needed!

## One-Time Setup (5 Minutes)

### Step 1: Install & Start

```bash
# Install Python dependencies (one time)
pip install -r requirements.txt

# Start the server
python api.py
```

That's it! The server will tell you when it's ready.

In another terminal:

```bash
# Install frontend dependencies (one time)
cd frontend
npm install

# Start the UI
npm start
```

Your browser will open automatically to `http://localhost:3000`

## Using Ibn Battuta (All in the UI!)

### 🔍 Search for Travel Options

1. **Fill out the search form:**
   - Departure city (e.g., "Toronto" or "YYZ")
   - Destination city (e.g., "London" or "LHR")
   - Customer location (where you're visiting)
   - Travel dates
   - Hotel budget (use the slider!)

2. **Click "Search Travel Options"**

3. **Browse results in 4 tabs:**
   - ✈️ Flights (Aeroplan-friendly highlighted!)
   - 🏨 Hotels (with favorite ❤️ buttons)
   - 🍽️ Restaurants (halal, upscale)
   - 🎭 Activities (culture, museums, nightlife)

### ❤️ Save Favorite Hotels

**When you find a hotel you love:**

1. Click the **heart icon** (❤️) on the hotel card
2. Done! It's now a favorite

**Next time you search that city:**
- Your favorite appears first (always #1!)
- Marked with "⭐️ YOUR FAVORITE!"
- No more searching for it again

### ⚙️ Manage Your Favorites

Click the **⚙️ Settings icon** in the top-right corner.

**In the Favorites tab:**
- See all your favorite hotels
- Add notes (e.g., "Room 302 has best view")
- Delete favorites you no longer need

### 📍 Add Your Favorite Places

**Why?** Hotels near your favorite coffee shops and restaurants rank higher!

Click the **⚙️ Settings icon** → **Saved Places tab**

**Option 1: Upload from Google Maps**

1. Go to [Google Takeout](https://takeout.google.com/)
2. Deselect all, select only **"Maps (your places)"**
3. Download the file
4. Click **"Upload JSON File"** and select it
5. Done! Hotels near these places now rank higher

**Option 2: Add Places Manually**

1. Click **"Add Place Manually"**
2. Fill in:
   - Name (e.g., "Blue Bottle Coffee")
   - Address
   - Type (cafe, restaurant, bar, etc.)
   - Coordinates (right-click on Google Maps to get them)
3. Click **"Add Place"**

**Result:** Hotels near your saved places get +50 points!

## Daily Usage (Super Simple!)

### Before a Trip

1. **Open Ibn Battuta**: `http://localhost:3000`
2. **Enter trip details** in the search form
3. **Click Search**
4. **Review results** - favorites and nearby saved places rank higher!
5. **Click ❤️** on any great hotels to remember them

### Managing Your Data

**View Favorites:**
- Click ⚙️ → Favorites tab
- See all saved hotels by city
- Add notes, delete old ones

**View Saved Places:**
- Click ⚙️ → Saved Places tab
- See your uploaded places
- Add more anytime

## Pro Tips

### 1. Build Your Favorites List
Every time you stay somewhere great, click ❤️. After a few trips, you'll have favorites in major cities and never waste time searching again!

### 2. Import Your Google Maps Saves
If you're a foodie who saves restaurants on Google Maps, import them! Hotels in those neighborhoods will automatically rank higher.

### 3. Use the Budget Slider
Adjust the hotel budget slider to find options in your range. Hotels over budget get warnings, within budget get bonuses.

### 4. Add Notes to Favorites
Click ⚙️ → Favorites → Edit (✏️ icon) to add notes like:
- "Ask for corner room"
- "Great breakfast buffet"
- "Request late checkout"

## Troubleshooting

### "Can't connect to server"
Make sure `python api.py` is running in a terminal. You should see:
```
✓ API initialized successfully
Starting server on http://localhost:5000
```

### "Frontend won't load"
Make sure `npm start` is running in the `frontend` folder.

### "Search is slow"
First search takes 30-60 seconds (normal!). Searching multiple airports and analyzing hotels takes time. Be patient!

### "No favorites showing"
Click ⚙️ to check if favorites saved correctly. If not, try clicking the heart again.

### "Uploaded saved places but no effect"
Restart the server (`python api.py`) after uploading saved places.

## What Happens Behind the Scenes

### When You Favorite a Hotel ❤️
- Saved to `data/favorites.json`
- Next search in that city: +50 score points
- Always appears first

### When You Upload Saved Places 📍
- Saved to `data/saved_places.json`
- System finds clusters of your places
- Hotels within 2km get +50 points max
- More places nearby = higher score

### Smart Scoring
Every option is scored 0-150:
- **Base**: 50 points
- **Aeroplan airline**: +20
- **Favorite hotel**: +50
- **Near saved places**: +50
- **Budget fit**: +5
- **Great area**: +20
- **Excellent rating**: +30

Top scores appear first!

## Example Workflow

### First-Time User

**Day 1:**
1. Start server: `python api.py`
2. Start UI: `cd frontend && npm start`
3. Search: Toronto → London
4. Find great hotel, click ❤️
5. Note: "Great location near Canary Wharf"

**Day 30 (next London trip):**
1. Open UI
2. Search: Toronto → London
3. Your favorite appears first!
4. Book immediately, no searching needed

### Power User (with Google Maps saves)

**Setup:**
1. Export Google Maps saved places
2. Click ⚙️ → Saved Places → Upload
3. Upload your 50 favorite cafes/restaurants

**Every search:**
- Hotels near your saved places rank way higher
- Always stay in neighborhoods you love
- Never stuck in boring hotel areas!

**Example:**
```
You've saved 5 coffee shops in Shoreditch, London

Search London:
→ Hotel in Shoreditch: Score 120 (near your cafes!)
→ Hotel in Westminster: Score 70 (no saved places)

Result: Shoreditch hotel wins!
```

## No CLI Commands Needed!

Everything is in the UI:
- ✅ Search travel options
- ✅ Favorite hotels
- ✅ Upload saved places
- ✅ Manage favorites
- ✅ View saved places
- ✅ Edit notes

The only command you run is **`python api.py`** to start!

## Next Steps

**After getting comfortable:**
- Read [FAVORITES_AND_SAVED_PLACES.md](FAVORITES_AND_SAVED_PLACES.md) for advanced tips
- Check [WEB_UI_README.md](WEB_UI_README.md) for full feature list
- Explore config.yaml to customize preferences

**For now, just:**
1. Start server
2. Open UI
3. Search
4. Favorite hotels
5. Enjoy!

---

**Happy traveling!** ✈️🌍

Questions? Everything is clickable in the UI. No commands needed!
