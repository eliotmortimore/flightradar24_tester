#!/usr/bin/env python3
"""
FlightRadar24 API CLI Tester

A minimal CLI tool to query the official FlightRadar24 API and print JSON responses.

Usage:
    python fr24_tester.py --aircraft_type C17 --limit 20
    python fr24_tester.py --bounds 30,-120,40,-110 --limit 100
    python fr24_tester.py --registration N12345
    python fr24_tester.py  # Get top 50 aircraft worldwide
    python fr24_tester.py --use_env_key  # Use API key from .env file

Requirements:
    - requests library (install with: pip install -r requirements.txt)
    - python-dotenv for environment variables (install with: pip install python-dotenv)

API Documentation:
    https://fr24api.flightradar24.com/docs/getting-started

Note: 
    - Public API (default): No API key required
    - Premium API: Requires API key for advanced features
    - Use --use_env_key to access premium endpoints with API key from .env file

To extend this tool:
    - Add new filter parameters to fetch_aircraft_data()
    - Implement additional API endpoints (airports, flights, etc.)
    - Add data validation and error handling
    - Implement caching for repeated queries
"""

import argparse
import json
import os
import requests
from typing import Optional, Dict, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass


def fetch_aircraft_data(
    aircraft_type: Optional[str] = None,
    registration: Optional[str] = None,
    bounds: Optional[str] = None,
    limit: int = 50,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch live aircraft data from FlightRadar24 API.
    
    Args:
        aircraft_type: Filter by aircraft type (e.g., 'C17', 'KC135')
        registration: Filter by aircraft registration (e.g., 'N12345')
        bounds: Bounding box as 'minLat,minLon,maxLat,maxLon'
        limit: Maximum number of results to return
        api_key: Optional API key for premium features
    
    Returns:
        Dictionary containing the API response
    """
    # Choose API endpoint based on whether API key is provided
    if api_key:
        # Premium API endpoint (requires API key)
        base_url = "https://api.flightradar24.com/common/v1/search.json"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    else:
        # Public API endpoint (no API key required)
        base_url = "https://data-live.flightradar24.com/zones/fcgi/feed.js"
        headers = {}
    
    # Build query parameters
    params = {
        'bounds': bounds if bounds else '90,-180,-90,180',  # Worldwide by default
        'faa': '1',
        'mlat': '1',
        'flarm': '1',
        'adsb': '1',
        'gnd': '1',
        'air': '1',
        'vehicles': '1',
        'estimated': '1',
        'stats': '1'
    }
    
    try:
        # Make API request
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Extract aircraft data
        aircraft_list = []
        if 'aircraft' in data:
            for aircraft in data['aircraft']:
                # Apply filters if provided
                if aircraft_type and aircraft.get('aircraft_type') != aircraft_type:
                    continue
                if registration and aircraft.get('registration') != registration:
                    continue
                
                aircraft_list.append(aircraft)
                
                # Stop if we've reached the limit
                if len(aircraft_list) >= limit:
                    break
        
        return {
            'status': 'success',
            'count': len(aircraft_list),
            'aircraft': aircraft_list,
            'raw_response': data,
            'api_type': 'premium' if api_key else 'public'
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'API request failed: {str(e)}',
            'api_type': 'premium' if api_key else 'public'
        }
    except json.JSONDecodeError as e:
        return {
            'status': 'error',
            'message': f'Failed to parse JSON response: {str(e)}',
            'api_type': 'premium' if api_key else 'public'
        }


def get_api_key_from_env() -> Optional[str]:
    """Get API key from environment variable."""
    return os.getenv('FR24_API_KEY')


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Query FlightRadar24 API for live aircraft data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fr24_tester.py --aircraft_type C17 --limit 20
  python fr24_tester.py --bounds 30,-120,40,-110 --limit 100
  python fr24_tester.py --registration N12345
  python fr24_tester.py  # Get top 50 aircraft worldwide
  python fr24_tester.py --use_env_key  # Use API key from .env file
        """
    )
    
    parser.add_argument(
        '--aircraft_type',
        type=str,
        help='Filter by aircraft type (e.g., C17, KC135)'
    )
    
    parser.add_argument(
        '--registration',
        type=str,
        help='Filter by aircraft registration (e.g., N12345)'
    )
    
    parser.add_argument(
        '--bounds',
        type=str,
        help='Bounding box as minLat,minLon,maxLat,maxLon (e.g., 30,-120,40,-110)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of results to return (default: 50)'
    )
    
    parser.add_argument(
        '--use_env_key',
        action='store_true',
        help='Use FR24_API_KEY environment variable for API key'
    )
    
    args = parser.parse_args()
    
    # Determine which API key to use
    api_key = None
    if args.use_env_key:
        api_key = get_api_key_from_env()
        if not api_key:
            print("Error: FR24_API_KEY environment variable not set")
            return
    
    # Fetch aircraft data
    result = fetch_aircraft_data(
        aircraft_type=args.aircraft_type,
        registration=args.registration,
        bounds=args.bounds,
        limit=args.limit,
        api_key=api_key
    )
    
    # Pretty print the JSON response
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
