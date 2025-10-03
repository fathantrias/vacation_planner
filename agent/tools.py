"""
Custom tools for the vacation planner agent.
Each tool is decorated with @tool to be used by LangGraph's create_react_agent.
"""

import os
import json
import random
from pathlib import Path
from typing import Optional, List, Union
from langchain_core.tools import tool
from datetime import datetime


# Helper function to load data files
def load_json_data(filename: str):
    """Load mock data from JSON files."""
    data_dir = Path(__file__).parent.parent / "data"
    file_path = data_dir / filename
    with open(file_path, 'r') as f:
        return json.load(f)


@tool
def get_user_calendar(start_date: str, end_date: str) -> dict:
    """
    Retrieve user's calendar availability and blocked dates for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Dictionary containing available dates, blocked dates, and vacation preferences
    """
    try:
        calendar_data = load_json_data("user_calendar.json")
        
        # Filter availability for the requested date range
        available_dates = []
        blocked_dates = []
        
        for date_str, status in calendar_data["availability"].items():
            if start_date <= date_str <= end_date:
                if status == "available":
                    available_dates.append(date_str)
                else:
                    blocked_dates.append(date_str)
        
        # Filter relevant blocked events
        relevant_events = [
            event for event in calendar_data["blocked_events"]
            if start_date <= event["date"] <= end_date
        ]
        
        return {
            "available_dates": available_dates,
            "blocked_dates": blocked_dates,
            "blocked_events": relevant_events,
            "vacation_preferences": calendar_data["vacation_preferences"]
        }
    except Exception as e:
        return {"error": f"Failed to retrieve calendar: {str(e)}"}


@tool
def get_user_preferences() -> dict:
    """
    Fetch user's travel preferences including budget, destinations, interests, and accommodation preferences.
    
    Returns:
        Dictionary containing complete user preference profile
    """
    try:
        preferences = load_json_data("user_preferences.json")
        return preferences
    except Exception as e:
        return {"error": f"Failed to retrieve preferences: {str(e)}"}


@tool
def search_flights(
    origin: str,
    destination: str,
    passengers: int = 1,
    travel_class: str = "economy"
) -> dict:
    """
    Search for available flights based on criteria.
    Note: Flights are available every day within October-November 2025.
    
    Args:
        origin: Departure airport code (e.g., 'CGK') or city name (e.g., 'Jakarta')
        destination: Arrival airport code (e.g., 'DPS') or city name (e.g., 'Bali')
        passengers: Number of passengers (default: 1)
        travel_class: 'economy' or 'business' (default: 'economy')
        
    Returns:
        Dictionary containing list of matching flights
    """
    # City to airport code mapping
    city_to_airport = {
        "jakarta": "CGK",
        "bali": "DPS",
        "denpasar": "DPS",
        "tokyo": "NRT",
        "paris": "CDG",
        "barcelona": "BCN",
        "santorini": "JTR"
    }
    
    # Convert city names to airport codes if needed (case-insensitive)
    origin_code = city_to_airport.get(origin.lower(), origin.upper())
    destination_code = city_to_airport.get(destination.lower(), destination.upper())
    
    # Debug logging
    print(f"[DEBUG] search_flights called with: origin={origin}, destination={destination}, passengers={passengers}, travel_class={travel_class}")
    print(f"[DEBUG] Converted to codes: origin={origin_code}, destination={destination_code}")
    
    try:
        flights_data = load_json_data("flights_mock.json")
        
        # Filter flights by criteria
        matching_flights = []
        for flight in flights_data["flights"]:
            if (flight["origin"] == origin_code and 
                flight["destination"] == destination_code and
                flight["class"] == travel_class):
                
                # Calculate total price based on passengers
                flight_copy = flight.copy()
                flight_copy["total_price"] = flight["price"] * passengers
                flight_copy["passengers"] = passengers
                matching_flights.append(flight_copy)
        
        if not matching_flights:
            print(f"[DEBUG] No matching flights found. Available flights from {origin_code}: {[f['destination'] for f in flights_data['flights'] if f['origin'] == origin_code]}")
            return {
                "flights": [],
                "message": f"No flights found from {origin_code} to {destination_code}"
            }
        
        print(f"[DEBUG] Found {len(matching_flights)} matching flights")
        # Sort by price
        matching_flights.sort(key=lambda x: x["total_price"])
        
        return {"flights": matching_flights[:5], "total_results": len(matching_flights)}
    except Exception as e:
        print(f"[DEBUG] Exception in search_flights: {str(e)}")
        return {"error": f"Failed to search flights: {str(e)}"}


@tool
def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int = 1,
    min_rating: float = 4.0
) -> dict:
    """
    Search for available hotels at destination.
    
    Args:
        destination: Destination city name (e.g., 'Bali', 'Tokyo')
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default: 1)
        min_rating: Minimum hotel rating (default: 4.0)
        
    Returns:
        Dictionary containing list of matching hotels
    """
    # Debug logging
    print(f"[DEBUG] search_hotels called with: destination={destination}, check_in={check_in}, check_out={check_out}, guests={guests}, min_rating={min_rating}")
    
    try:
        hotels_data = load_json_data("hotels_mock.json")
        
        # Calculate number of nights
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        
        # Filter hotels by destination and rating
        matching_hotels = []
        for hotel in hotels_data["hotels"]:
            if (destination.lower() in hotel["destination_city"].lower() and
                hotel["rating"] >= min_rating):
                
                hotel_copy = hotel.copy()
                hotel_copy["nights"] = nights
                hotel_copy["total_price"] = hotel["price_per_night"] * nights
                hotel_copy["check_in"] = check_in
                hotel_copy["check_out"] = check_out
                matching_hotels.append(hotel_copy)
        
        if not matching_hotels:
            print(f"[DEBUG] No matching hotels found. Available cities: {list(set([h['destination_city'] for h in hotels_data['hotels']]))}")
            return {
                "hotels": [],
                "message": f"No hotels found in {destination} meeting criteria"
            }
        
        print(f"[DEBUG] Found {len(matching_hotels)} matching hotels")
        # Sort by rating (descending) then price (ascending)
        matching_hotels.sort(key=lambda x: (-x["rating"], x["total_price"]))
        
        return {"hotels": matching_hotels[:5], "total_results": len(matching_hotels)}
    except Exception as e:
        print(f"[DEBUG] Exception in search_hotels: {str(e)}")
        return {"error": f"Failed to search hotels: {str(e)}"}


@tool
def search_activities(
    destination: str,
    interests: Optional[Union[List[str], str]] = None
) -> dict:
    """
    Find activities and attractions at destination.
    Note: Activities are available every day within October-November 2025.
    
    Args:
        destination: Destination city name (e.g., 'Bali', 'Tokyo')
        interests: Optional list of interest categories (e.g., ['beaches', 'culture']) or string
        
    Returns:
        Dictionary containing list of matching activities
    """
    # Auto-fix: Convert JSON string to list if needed
    if isinstance(interests, str):
        print(f"[DEBUG] Detected string interests: {interests}")
        if interests.startswith('['):
            try:
                interests = json.loads(interests)
                print(f"[DEBUG] Converted to list: {interests}")
            except json.JSONDecodeError:
                print(f"[DEBUG] Failed to parse JSON string, treating as None")
                interests = None
        else:
            # Single interest as string, convert to list
            interests = [interests]
            print(f"[DEBUG] Converted single string to list: {interests}")
    
    # Debug logging
    print(f"[DEBUG] search_activities processing with: destination={destination}, interests={interests} (type: {type(interests)})")
    
    try:
        activities_data = load_json_data("activities_mock.json")
        
        # Filter activities by destination (all activities available any day)
        matching_activities = []
        for activity in activities_data["activities"]:
            if destination.lower() in activity["destination_city"].lower():
                # Filter by interests if provided
                if interests:
                    if activity["category"] in interests:
                        matching_activities.append(activity)
                else:
                    matching_activities.append(activity)
        
        if not matching_activities:
            print(f"[DEBUG] No matching activities found. Available cities: {list(set([a['destination_city'] for a in activities_data['activities']]))}")
            return {
                "activities": [],
                "message": f"No activities found in {destination}"
            }
        
        print(f"[DEBUG] Found {len(matching_activities)} matching activities")
        # Sort by rating
        matching_activities.sort(key=lambda x: -x["rating"])
        
        return {"activities": matching_activities[:10], "total_results": len(matching_activities)}
    except Exception as e:
        print(f"[DEBUG] Exception in search_activities: {str(e)}")
        return {"error": f"Failed to search activities: {str(e)}"}


@tool
def calculate_budget(planned_expenses: str) -> dict:
    """
    Calculate total expenses and validate against user's budget.
    Input should be a JSON string of expenses array.
    Note: Activities are not included as they are booked separately by users.
    
    Args:
        planned_expenses: JSON string of expenses list, e.g. '[{"category":"flights","amount":850}]'
        
    Returns:
        Budget analysis with warnings and validation status
    """
    try:
        # Parse the expenses
        expenses = json.loads(planned_expenses)
        
        # Get user's budget from preferences
        preferences = load_json_data("user_preferences.json")
        budget_limits = preferences["budget"]
        
        # Calculate totals by category (excluding activities - they're not bookable)
        totals = {"flights": 0, "hotels": 0}
        for expense in expenses:
            category = expense["category"]
            if category in totals:
                totals[category] += expense["amount"]
            # Ignore any activity expenses if mistakenly included
        
        total_spent = sum(totals.values())
        remaining = budget_limits["total"] - total_spent
        within_budget = total_spent <= budget_limits["total"]
        
        # Check category-specific limits (only for bookable items)
        warnings = []
        for category, spent in totals.items():
            if category in budget_limits["breakdown"]:
                limit = budget_limits["breakdown"][category]
                if spent > limit:
                    warnings.append(
                        f"{category.capitalize()} exceeds budget: ${spent:.2f} > ${limit:.2f}"
                    )
        
        if not within_budget:
            warnings.append(
                f"Total budget exceeded by ${abs(remaining):.2f}"
            )
        
        return {
            "total_spent": round(total_spent, 2),
            "budget_limit": budget_limits["total"],
            "remaining": round(remaining, 2),
            "breakdown": totals,
            "within_budget": within_budget,
            "warnings": warnings,
            "currency": budget_limits["currency"],
            "note": "Activities not included - book directly with providers"
        }
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format for planned_expenses"}
    except Exception as e:
        return {"error": f"Failed to calculate budget: {str(e)}"}


@tool
def book_flight(flight_id: str) -> dict:
    """
    Book a flight. Requires payment authorization.
    Note: For PoC/single-user deployment, payment authorization is tracked via environment variable.
    
    Args:
        flight_id: Flight ID from search results (e.g., 'FL001')
        
    Returns:
        Booking confirmation or error message
    """
    try:
        # Check payment authorization via environment variable
        # This approach works for single-user/session deployment (PoC)
        # For multi-user production, use session-based storage or database
        payment_authorized = os.environ.get('PAYMENT_AUTHORIZED') == 'true'
        
        if not payment_authorized:
            return {
                "booking_status": "failed",
                "message": "⚠️ Payment information required. Please configure payment details in the sidebar first.",
                "action_required": "setup_payment"
            }
        
        # Find the flight
        flights_data = load_json_data("flights_mock.json")
        flight = next((f for f in flights_data["flights"] if f["flight_id"] == flight_id), None)
        
        if not flight:
            return {
                "booking_status": "failed",
                "message": f"Flight {flight_id} not found"
            }
        
        # Mock booking (in real system, this would call booking API)
        booking_reference = f"BK-{flight_id}-{random.randint(1000, 9999)}"
        
        return {
            "booking_status": "confirmed",
            "booking_reference": booking_reference,
            "flight_details": {
                "flight_id": flight["flight_id"],
                "airline": flight["airline"],
                "route": f"{flight['origin_city']} → {flight['destination_city']}",
                "duration": flight["duration"]
            },
            "total_charged": flight["price"],
            "currency": flight["currency"],
            "message": f"✅ Flight booked successfully! Confirmation: {booking_reference}"
        }
    except Exception as e:
        return {"booking_status": "failed", "error": f"Booking failed: {str(e)}"}


@tool
def book_hotel(hotel_id: str, check_in: str, check_out: str) -> dict:
    """
    Book a hotel. Requires payment authorization.
    Note: For PoC/single-user deployment, payment authorization is tracked via environment variable.
    
    Args:
        hotel_id: Hotel ID from search results (e.g., 'HTL001')
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        
    Returns:
        Booking confirmation or error message
    """
    try:
        # Check payment authorization via environment variable
        # This approach works for single-user/session deployment (PoC)
        # For multi-user production, use session-based storage or database
        payment_authorized = os.environ.get('PAYMENT_AUTHORIZED') == 'true'
        
        if not payment_authorized:
            return {
                "booking_status": "failed",
                "message": "⚠️ Payment information required. Please configure payment details in the sidebar first.",
                "action_required": "setup_payment"
            }
        
        # Find the hotel
        hotels_data = load_json_data("hotels_mock.json")
        hotel = next((h for h in hotels_data["hotels"] if h["hotel_id"] == hotel_id), None)
        
        if not hotel:
            return {
                "booking_status": "failed",
                "message": f"Hotel {hotel_id} not found"
            }
        
        # Calculate nights and total
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        total_price = hotel["price_per_night"] * nights
        
        # Mock booking
        booking_reference = f"BK-{hotel_id}-{random.randint(1000, 9999)}"
        
        return {
            "booking_status": "confirmed",
            "booking_reference": booking_reference,
            "hotel_details": {
                "hotel_id": hotel["hotel_id"],
                "name": hotel["name"],
                "location": hotel["location"],
                "room_type": hotel["room_type"],
                "rating": hotel["rating"]
            },
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "total_charged": total_price,
            "currency": hotel["currency"],
            "message": f"✅ Hotel booked successfully! Confirmation: {booking_reference}"
        }
    except Exception as e:
        return {"booking_status": "failed", "error": f"Booking failed: {str(e)}"}


# Export all tools
VACATION_PLANNER_TOOLS = [
    get_user_calendar,
    get_user_preferences,
    search_flights,
    search_hotels,
    search_activities,
    calculate_budget,
    book_flight,
    book_hotel
]
