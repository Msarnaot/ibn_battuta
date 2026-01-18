"""
Utility functions for the Ibn Battuta travel automation system
"""

import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_env_vars() -> Dict[str, str]:
    """Load environment variables"""
    load_dotenv()

    return {
        'google_maps_api_key': os.getenv('GOOGLE_MAPS_API_KEY'),
        'amadeus_api_key': os.getenv('AMADEUS_API_KEY'),
        'amadeus_api_secret': os.getenv('AMADEUS_API_SECRET'),
        'yelp_api_key': os.getenv('YELP_API_KEY'),
    }


def validate_api_keys(env_vars: Dict[str, str]) -> bool:
    """Validate that required API keys are present"""
    required_keys = ['google_maps_api_key', 'amadeus_api_key', 'amadeus_api_secret']

    missing_keys = [key for key in required_keys if not env_vars.get(key)]

    if missing_keys:
        print(f"⚠️  Missing required API keys: {', '.join(missing_keys)}")
        print("Please set these in your .env file")
        return False

    return True


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'CAD': 'CA$',
    }

    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable format"""
    hours = minutes // 60
    mins = minutes % 60

    if hours > 0 and mins > 0:
        return f"{hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"


def format_distance(meters: float) -> str:
    """Format distance in meters to human readable format"""
    km = meters / 1000

    if km < 1:
        return f"{int(meters)}m"
    else:
        return f"{km:.1f}km"


def calculate_price_difference_percent(price1: float, price2: float) -> float:
    """Calculate percentage difference between two prices"""
    if price1 == 0:
        return 0

    return ((price2 - price1) / price1) * 100


def is_major_city(city_name: str) -> bool:
    """Check if a city is considered a major city"""
    major_cities = [
        'london', 'paris', 'munich', 'amsterdam', 'berlin', 'rome', 'madrid',
        'barcelona', 'vienna', 'prague', 'budapest', 'copenhagen', 'stockholm',
        'oslo', 'helsinki', 'dublin', 'brussels', 'zurich', 'geneva', 'milan',
        'new york', 'los angeles', 'chicago', 'san francisco', 'boston',
        'washington', 'seattle', 'toronto', 'vancouver', 'montreal', 'tokyo',
        'singapore', 'hong kong', 'dubai', 'sydney', 'melbourne'
    ]

    return city_name.lower() in major_cities
