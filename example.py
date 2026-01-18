#!/usr/bin/env python3
"""
Example script showing how to use Ibn Battuta programmatically
"""

from main import TravelAutomation
from datetime import datetime, timedelta

def main():
    """Run example searches"""
    # Initialize the system
    automation = TravelAutomation()

    # Example 1: Business trip to London
    print("\n" + "="*80)
    print("EXAMPLE 1: Business trip from Toronto to London")
    print("="*80)

    automation.run_automated(
        origin="Toronto",
        destination="London",
        customer_location="Canary Wharf, London",
        departure_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        return_date=(datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d")
    )

    # Example 2: Trip to Munich
    print("\n" + "="*80)
    print("EXAMPLE 2: Business trip from New York to Munich")
    print("="*80)

    automation.run_automated(
        origin="JFK",
        destination="Munich",
        customer_location="Munich City Center",
        departure_date=(datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
        return_date=(datetime.now() + timedelta(days=24)).strftime("%Y-%m-%d")
    )

    # Example 3: One-way trip
    print("\n" + "="*80)
    print("EXAMPLE 3: One-way trip from San Francisco to Seattle")
    print("="*80)

    automation.run_automated(
        origin="SFO",
        destination="Seattle",
        customer_location="Downtown Seattle",
        departure_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        return_date=None
    )


if __name__ == "__main__":
    main()
