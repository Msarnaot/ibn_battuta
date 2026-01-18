#!/usr/bin/env python3
"""
Ibn Battuta - Automated Travel Booking System
Main entry point for the application
"""

import sys
import argparse
from datetime import datetime, timedelta
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from src.utils import load_config, load_env_vars, validate_api_keys
from src.distance_calculator import DistanceCalculator
from src.flight_search import FlightSearcher
from src.hotel_search import HotelSearcher
from src.recommendations import RecommendationEngine


console = Console()


class TravelAutomation:
    """Main orchestrator for travel automation"""

    def __init__(self):
        """Initialize the travel automation system"""
        # Load configuration
        console.print("[cyan]Loading configuration...[/cyan]")
        self.config = load_config()

        # Load environment variables
        self.env_vars = load_env_vars()

        # Validate API keys
        if not validate_api_keys(self.env_vars):
            console.print("[red]❌ Missing required API keys. Please check your .env file.[/red]")
            console.print("[yellow]Copy .env.example to .env and add your API keys.[/yellow]")
            sys.exit(1)

        # Initialize components
        console.print("[cyan]Initializing components...[/cyan]")

        self.distance_calc = DistanceCalculator(self.env_vars['google_maps_api_key'])

        self.flight_searcher = FlightSearcher(
            self.env_vars['amadeus_api_key'],
            self.env_vars['amadeus_api_secret'],
            self.distance_calc,
            self.config
        )

        self.hotel_searcher = HotelSearcher(
            self.env_vars['google_maps_api_key'],
            self.distance_calc,
            self.config
        )

        self.recommendation_engine = RecommendationEngine(
            self.env_vars['google_maps_api_key'],
            self.distance_calc,
            self.config
        )

        console.print("[green]✓ Initialization complete![/green]\n")

    def run_interactive(self):
        """Run interactive mode"""
        console.print(Panel.fit(
            "[bold cyan]Ibn Battuta - Automated Travel Booking System[/bold cyan]\n"
            "[dim]Named after the famous medieval traveler[/dim]",
            border_style="cyan"
        ))

        # Get trip details
        console.print("\n[bold]Trip Details[/bold]")
        console.print("-" * 50)

        origin = Prompt.ask("📍 Departure city or airport code")
        destination = Prompt.ask("📍 Destination city or airport code")
        customer_location = Prompt.ask("🏢 Customer location (address or area)", default=destination)

        # Dates
        console.print("\n[bold]Travel Dates[/bold]")
        departure_date = Prompt.ask(
            "📅 Departure date (YYYY-MM-DD)",
            default=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        )

        is_round_trip = Confirm.ask("🔄 Round trip?", default=True)
        return_date = None

        if is_round_trip:
            return_date = Prompt.ask(
                "📅 Return date (YYYY-MM-DD)",
                default=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
            )

        # Hotel dates
        check_in = departure_date
        check_out = return_date if return_date else (datetime.strptime(departure_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d")

        console.print("\n[bold cyan]Starting search...[/bold cyan]\n")

        # Search flights
        console.print(Panel("[bold]Phase 1: Flight Search[/bold]", border_style="blue"))
        flights = self.flight_searcher.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=1
        )

        # Check business class upgrades
        if flights:
            flights = self.flight_searcher.check_business_class_upgrade(flights)
            console.print(self.flight_searcher.format_flight_results(flights))

        # Search hotels
        console.print(Panel("[bold]Phase 2: Hotel Search[/bold]", border_style="blue"))

        # Ask user about preferred distance from customer
        console.print(f"\n[yellow]Customer location is: {customer_location}[/yellow]")

        use_custom_location = Confirm.ask(
            "Would you prefer to stay in a different area (e.g., major city nearby)?",
            default=False
        )

        hotel_search_location = destination
        if use_custom_location:
            hotel_search_location = Prompt.ask(
                "Where would you like to search for hotels?",
                default=destination
            )

        hotels = self.hotel_searcher.search_hotels(
            destination=hotel_search_location,
            customer_location=customer_location,
            check_in_date=check_in,
            check_out_date=check_out
        )

        # Get car rental recommendation
        car_rental_info = self.hotel_searcher.get_car_rental_recommendation(
            hotel_search_location,
            customer_location
        )

        if hotels:
            console.print(self.hotel_searcher.format_hotel_results(hotels, car_rental_info))

            # Get recommendations for top hotel
            if Confirm.ask("\n🍽️  Get restaurant and activity recommendations?", default=True):
                top_hotel = hotels[0]

                console.print(Panel("[bold]Phase 3: Recommendations[/bold]", border_style="blue"))

                # Restaurants
                restaurants = self.recommendation_engine.get_restaurant_recommendations(
                    top_hotel['address']
                )

                console.print(self.recommendation_engine.format_restaurant_results(restaurants))

                # Activities
                activities = self.recommendation_engine.get_activity_recommendations(
                    top_hotel['address']
                )

                console.print(self.recommendation_engine.format_activity_results(activities))

        # Summary
        self._print_summary(flights, hotels, car_rental_info)

    def run_automated(self, origin: str, destination: str, customer_location: str,
                     departure_date: str, return_date: Optional[str] = None):
        """Run automated mode (non-interactive)"""
        console.print(Panel.fit(
            "[bold cyan]Ibn Battuta - Automated Travel Booking System[/bold cyan]",
            border_style="cyan"
        ))

        console.print(f"\n🔍 Searching travel options:")
        console.print(f"   From: {origin}")
        console.print(f"   To: {destination}")
        console.print(f"   Customer at: {customer_location}")
        console.print(f"   Departure: {departure_date}")
        if return_date:
            console.print(f"   Return: {return_date}")

        # Search flights
        console.print(Panel("[bold]Phase 1: Flight Search[/bold]", border_style="blue"))
        flights = self.flight_searcher.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=1
        )

        if flights:
            flights = self.flight_searcher.check_business_class_upgrade(flights)
            console.print(self.flight_searcher.format_flight_results(flights))

        # Search hotels
        console.print(Panel("[bold]Phase 2: Hotel Search[/bold]", border_style="blue"))

        check_in = departure_date
        check_out = return_date if return_date else (datetime.strptime(departure_date, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d")

        hotels = self.hotel_searcher.search_hotels(
            destination=destination,
            customer_location=customer_location,
            check_in_date=check_in,
            check_out_date=check_out
        )

        car_rental_info = self.hotel_searcher.get_car_rental_recommendation(
            destination,
            customer_location
        )

        if hotels:
            console.print(self.hotel_searcher.format_hotel_results(hotels, car_rental_info))

            # Get recommendations for top hotel
            console.print(Panel("[bold]Phase 3: Recommendations[/bold]", border_style="blue"))

            top_hotel = hotels[0]

            # Restaurants
            restaurants = self.recommendation_engine.get_restaurant_recommendations(
                top_hotel['address']
            )

            console.print(self.recommendation_engine.format_restaurant_results(restaurants))

            # Activities
            activities = self.recommendation_engine.get_activity_recommendations(
                top_hotel['address']
            )

            console.print(self.recommendation_engine.format_activity_results(activities))

        # Summary
        self._print_summary(flights, hotels, car_rental_info)

    def _print_summary(self, flights, hotels, car_rental_info):
        """Print summary of results"""
        console.print("\n" + "="*80)
        console.print("[bold cyan]SUMMARY[/bold cyan]")
        console.print("="*80)

        summary_table = Table(show_header=False, box=None)

        summary_table.add_row("✈️  Flights found:", f"[green]{len(flights)}[/green]")
        summary_table.add_row("🏨 Hotels found:", f"[green]{len(hotels)}[/green]")

        if car_rental_info and car_rental_info['recommended']:
            summary_table.add_row("🚗 Car rental:", "[yellow]Recommended[/yellow]")
        else:
            summary_table.add_row("🚗 Car rental:", "[green]Not needed[/green]")

        console.print(summary_table)

        console.print("\n[bold green]✓ Search complete![/bold green]")
        console.print("\n[dim]Next steps:")
        console.print("1. Review the options above")
        console.print("2. Book your preferred flight and hotel")
        console.print("3. Add recommended restaurants to your itinerary[/dim]")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Ibn Battuta - Automated Travel Booking System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py

  # Automated mode
  python main.py --origin "New York" --destination "London" --customer "Central London" --departure 2024-03-15 --return 2024-03-20

  # One-way trip
  python main.py --origin YYZ --destination SFO --customer "San Francisco" --departure 2024-03-15
        """
    )

    parser.add_argument('--origin', help='Departure city or airport code')
    parser.add_argument('--destination', help='Destination city or airport code')
    parser.add_argument('--customer', help='Customer location')
    parser.add_argument('--departure', help='Departure date (YYYY-MM-DD)')
    parser.add_argument('--return', dest='return_date', help='Return date (YYYY-MM-DD)')

    args = parser.parse_args()

    try:
        automation = TravelAutomation()

        # Check if running in automated or interactive mode
        if args.origin and args.destination and args.customer and args.departure:
            # Automated mode
            automation.run_automated(
                origin=args.origin,
                destination=args.destination,
                customer_location=args.customer,
                departure_date=args.departure,
                return_date=args.return_date
            )
        else:
            # Interactive mode
            automation.run_interactive()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Search cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
