# Ibn Battuta - MacBook Setup Guide

Complete setup instructions for running Ibn Battuta on your MacBook using Conda (your system Python stays untouched!)

## Prerequisites

Before you begin, make sure you have:

### 1. Homebrew (macOS package manager)
```bash
# Check if installed
brew --version

# If not installed, install it:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Node.js and npm
```bash
# Check if installed
node --version
npm --version

# If not installed:
brew install node
```

### 3. Conda (Miniconda or Anaconda)
```bash
# Check if installed
conda --version

# If not installed, download and install Miniconda:
# Visit: https://docs.conda.io/en/latest/miniconda.html
# Or use Homebrew:
brew install --cask miniconda

# After installation, initialize conda:
conda init zsh  # or 'bash' if you use bash
# Then restart your terminal
```

## Quick Setup (5 Minutes)

### Step 1: Clone the Repository

If you haven't already:
```bash
git clone <your-repo-url>
cd ibn_battuta
```

### Step 2: Run Setup Script

```bash
./setup_mac.sh
```

This script will:
- Create a conda environment named `ibn_battuta`
- Install all Python dependencies
- Install all frontend (React) dependencies
- Create a `.env` file for your API keys

### Step 3: Add Your API Keys

Edit the `.env` file and add your API keys:

```bash
# Open in your favorite editor
nano .env
# or
code .env
# or
open -e .env
```

Add your keys:
```env
GOOGLE_MAPS_API_KEY=your_actual_google_maps_key_here
AMADEUS_API_KEY=your_actual_amadeus_key_here
AMADEUS_API_SECRET=your_actual_amadeus_secret_here
```

**Where to get API keys:**

#### Google Maps API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable these APIs:
   - Maps JavaScript API
   - Places API
   - Distance Matrix API
   - Geocoding API
4. Go to Credentials → Create Credentials → API Key
5. Copy your API key

#### Amadeus API Credentials
1. Go to [Amadeus for Developers](https://developers.amadeus.com/)
2. Create a free account
3. Create a new app
4. Copy your API Key and API Secret

### Step 4: Start the Application

```bash
./start.sh
```

This will:
- Start the backend server on `http://localhost:5000`
- Start the frontend React app on `http://localhost:3000`
- Automatically open your browser

## Manual Setup (If You Prefer)

### 1. Create Conda Environment

```bash
conda create -n ibn_battuta python=3.11 -y
conda activate ibn_battuta
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Create and Configure .env

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 5. Start Backend (Terminal 1)

```bash
conda activate ibn_battuta
python api.py
```

### 6. Start Frontend (Terminal 2)

```bash
cd frontend
npm start
```

## Daily Usage

After initial setup, starting Ibn Battuta is simple:

### Option 1: Use the Start Script (Easiest)
```bash
./start.sh
```

### Option 2: Manual Start

Terminal 1 (Backend):
```bash
conda activate ibn_battuta
python api.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

Then open `http://localhost:3000` in your browser.

## Stopping the Application

If using `./start.sh`:
- Press `Ctrl+C` in the terminal

If running manually:
- Press `Ctrl+C` in each terminal window

## Updating the Application

Pull latest changes:
```bash
git pull origin main
```

Update dependencies if needed:
```bash
conda activate ibn_battuta
pip install -r requirements.txt --upgrade
cd frontend
npm install
cd ..
```

## Troubleshooting

### "conda: command not found"

**Solution:** Install Miniconda or Anaconda, then restart your terminal.

```bash
brew install --cask miniconda
conda init zsh  # or bash
# Restart terminal
```

### "npm: command not found"

**Solution:** Install Node.js

```bash
brew install node
```

### "Can't connect to server" in the web UI

**Solution:** Make sure the backend is running

```bash
# In a terminal:
conda activate ibn_battuta
python api.py
```

You should see:
```
✓ API initialized successfully
Starting server on http://localhost:5000
```

### Frontend won't start

**Solution:** Make sure npm dependencies are installed

```bash
cd frontend
npm install
npm start
```

### "ModuleNotFoundError" when running backend

**Solution:** Make sure conda environment is activated and dependencies are installed

```bash
conda activate ibn_battuta
pip install -r requirements.txt
```

### API errors or "No results found"

**Solution:** Check your API keys in `.env`

1. Make sure `.env` file exists in the root directory
2. Verify your API keys are correct (no extra spaces, complete keys)
3. Make sure you've enabled the required APIs in Google Cloud Console
4. Check Amadeus API quota (free tier has limits)

## Conda Environment Management

### Activate environment
```bash
conda activate ibn_battuta
```

### Deactivate environment
```bash
conda deactivate
```

### List all environments
```bash
conda env list
```

### Remove environment (if you want to start fresh)
```bash
conda remove -n ibn_battuta --all
```

### Export environment (for backup)
```bash
conda activate ibn_battuta
conda env export > environment.yml
```

## What Gets Installed (For Your Reference)

### Python Packages (in conda env only):
- requests - HTTP library
- python-dotenv - Environment variable management
- pyyaml - YAML parser
- googlemaps - Google Maps API client
- amadeus - Amadeus API client
- beautifulsoup4 - HTML parser
- lxml - XML/HTML parser
- selenium - Browser automation
- webdriver-manager - WebDriver management
- rich - Terminal formatting
- geopy - Geocoding library
- flask - Web framework
- flask-cors - CORS support

### Frontend Packages (in node_modules):
- react - UI framework
- react-dom - React DOM renderer
- axios - HTTP client
- @mui/material - Material-UI components
- @emotion/react - CSS-in-JS
- date-fns - Date utilities

## System Requirements

- macOS 10.14 or later
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection (for API calls)

## Architecture

```
ibn_battuta/
├── api.py              # Flask backend server
├── main.py             # CLI interface (optional)
├── config.yaml         # User preferences
├── .env                # API keys (DO NOT commit!)
├── src/                # Backend Python modules
├── frontend/           # React web application
│   ├── src/
│   ├── public/
│   └── package.json
├── setup_mac.sh        # Automated setup script
├── start.sh            # Easy start script
└── requirements.txt    # Python dependencies
```

## Next Steps

1. ✅ Complete setup
2. ✅ Add API keys
3. 📖 Read [GETTING_STARTED_UI.md](GETTING_STARTED_UI.md) - Learn how to use the web interface
4. 📖 Read [FAVORITES_AND_SAVED_PLACES.md](FAVORITES_AND_SAVED_PLACES.md) - Advanced features
5. 🎨 Customize `config.yaml` with your travel preferences
6. ✈️ Start planning trips!

## Need Help?

- Check [README.md](README.md) for full documentation
- Check [QUICKSTART.md](QUICKSTART.md) for CLI usage
- Check [WEB_UI_README.md](WEB_UI_README.md) for web UI features

---

Happy travels! ✈️🌍
