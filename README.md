# ipview

Analyze firewall logs and visualize blocked IP addresses on a world map.

## Installation

```bash
pip install -e .
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage (scans *.log files, outputs ip_map.png)
python -m ipview

# Specify input pattern and output file
python -m ipview -i "logdir/*" -o map.png

# Generate an interactive HTML map with zoom/pan (uses file modification time as timestamp)
python -m ipview -i "logdir/*" --html -o map.html

# Generate a density heatmap
python -m ipview -i "logdir/*" --heatmap -o heatmap.png

# Verbose mode
python -m ipview -i "logdir/*" -v
```

## Timestamps

When analyzing log directories, timestamps are extracted from the file modification time of each log file, allowing you to track when IPs were first seen over time.

## GeoIP Database

This tool requires the MaxMind GeoLite2 City database. Download it from:
https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

Set the path via environment variable or command line:

```bash
export GEOIP_DB_PATH=/path/to/GeoLite2-City.mmdb
python -m ipview --geo-db /path/to/GeoLite2-City.mmdb
```
