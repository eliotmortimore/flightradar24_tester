# FlightRadar24 API CLI Tester

A minimal Python CLI tool to query the official FlightRadar24 API and print JSON responses.

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Examples

Get top 50 aircraft worldwide:

```bash
python fr24_tester.py
```

Filter by aircraft type:

```bash
python fr24_tester.py --aircraft_type C17 --limit 20
python fr24_tester.py --aircraft_type KC135 --limit 10
```

Filter by aircraft registration:

```bash
python fr24_tester.py --registration N12345
```

Query specific geographic bounds:

```bash
python fr24_tester.py --bounds 30,-120,40,-110 --limit 100
```

### Command Line Options

- `--aircraft_type`: Filter by aircraft type (e.g., C17, KC135)
- `--registration`: Filter by aircraft registration (e.g., N12345)
- `--bounds`: Bounding box as minLat,minLon,maxLat,maxLon (e.g., 30,-120,40,-110)
- `--limit`: Maximum number of results to return (default: 50)

## Output

The tool outputs JSON with the following structure:

```json
{
  "status": "success",
  "count": 25,
  "aircraft": [...],
  "raw_response": {...}
}
```

## API Documentation

For more information about the FlightRadar24 API:
https://fr24api.flightradar24.com/docs/getting-started

## Extending the Tool

To add more functionality:

- Add new filter parameters to `fetch_aircraft_data()`
- Implement additional API endpoints (airports, flights, etc.)
- Add data validation and error handling
- Implement caching for repeated queries
