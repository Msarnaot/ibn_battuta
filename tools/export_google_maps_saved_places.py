#!/usr/bin/env python3
"""
Helper tool to create saved_places.json from Google Maps export

Usage:
1. Go to Google Takeout: https://takeout.google.com/
2. Select only "Maps (your places)"
3. Download the export
4. Extract the JSON file
5. Run this script: python tools/export_google_maps_saved_places.py <path-to-saved-places.json>

OR manually create a JSON file with this format:
[
    {
        "name": "Blue Bottle Coffee",
        "address": "123 Main St, San Francisco, CA",
        "type": "cafe",
        "coordinates": {"lat": 37.7749, "lng": -122.4194}
    },
    ...
]
"""

import json
import sys
import os


def convert_google_takeout_format(input_file: str, output_file: str = "data/saved_places.json"):
    """
    Convert Google Takeout saved places to Ibn Battuta format

    Google Takeout format is complex - this is a simplified converter
    """
    print(f"Reading {input_file}...")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        converted_places = []

        # Google Takeout format varies, try to handle common structures
        if 'features' in data:  # GeoJSON format
            for feature in data['features']:
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})

                place = {
                    'name': props.get('name', props.get('title', 'Unknown')),
                    'address': props.get('address', props.get('location', {}).get('address', '')),
                    'type': props.get('type', 'other'),
                    'coordinates': {}
                }

                if geom and geom.get('coordinates'):
                    coords = geom['coordinates']
                    place['coordinates'] = {
                        'lat': coords[1] if len(coords) > 1 else 0,
                        'lng': coords[0] if len(coords) > 0 else 0
                    }

                if place['name'] != 'Unknown':
                    converted_places.append(place)

        else:  # Try generic format
            # Assuming it's a list or dict with places
            places_list = data if isinstance(data, list) else data.get('places', [])

            for item in places_list:
                if isinstance(item, dict):
                    place = {
                        'name': item.get('name', item.get('title', 'Unknown')),
                        'address': item.get('address', item.get('formatted_address', '')),
                        'type': item.get('type', 'other'),
                        'coordinates': item.get('coordinates', item.get('geometry', {}).get('location', {}))
                    }

                    if place['name'] != 'Unknown':
                        converted_places.append(place)

        # Save to output file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted_places, f, indent=2, ensure_ascii=False)

        print(f"✓ Converted {len(converted_places)} places")
        print(f"✓ Saved to {output_file}")

        return converted_places

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the file is valid JSON")
        print("2. Try manually creating the file in the format shown above")
        print("3. Or use the web UI to upload places one by one")
        return []


def create_sample_file(output_file: str = "data/saved_places_example.json"):
    """Create a sample file to show the format"""
    sample = [
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
            "name": "The French Laundry",
            "address": "6640 Washington St, Yountville, CA 94599",
            "type": "restaurant",
            "coordinates": {"lat": 38.4039, "lng": -122.3631}
        }
    ]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample, f, indent=2)

    print(f"✓ Created example file: {output_file}")
    print("\nEdit this file with your saved places, then copy to data/saved_places.json")


def main():
    """Main entry point"""
    print("=" * 70)
    print("Ibn Battuta - Google Maps Saved Places Converter")
    print("=" * 70)
    print()

    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  python {sys.argv[0]} <google-takeout-file.json>")
        print(f"  python {sys.argv[0]} --example  # Create example file")
        print()
        print("Or create data/saved_places.json manually with this format:")
        print("""
[
    {
        "name": "Place Name",
        "address": "123 Main St, City, State ZIP",
        "type": "cafe",  // or "restaurant", "bar", "museum", etc.
        "coordinates": {"lat": 37.7749, "lng": -122.4194}
    }
]
""")
        sys.exit(1)

    if sys.argv[1] == '--example':
        create_sample_file()
        sys.exit(0)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)

    convert_google_takeout_format(input_file)


if __name__ == '__main__':
    main()
