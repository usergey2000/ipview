# ipview

Analyze firewall logs and visualize blocked IP addresses on a world map.

## Features

- Parse firewall logs (iptables, syslog format)
- Extract IPs from DROP entries
- Geolocate IPs using MaxMind GeoIP
- Generate PNG maps with cartopy
- Create interactive HTML maps with Leaflet.js

## Installation

```bash
pip3 install -e .
```

## Usage

```bash
# Basic usage
python3 -m ipview

# With verbose output
python3 -m ipview --verbose

# Generate HTML map
python3 -m ipview --html -o map.html
```

## Project Structure

```
ipview/
├── ipview/            # Python package
│   ├── __init__.py
│   ├── collector.py   # Parse DROP entries from log files
│   ├── geo.py         # Geolocate IPs using MaxMind GeoIP
│   ├── map.py         # Generate PNG and HTML maps
│   └── main.py        # CLI entry point
├── ipt.log            # Sample iptables config (not actual log data)
├── requirements.txt   # Python dependencies
└── pyproject.toml     # Package configuration
```
