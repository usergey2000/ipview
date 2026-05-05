# ipview

Analyze firewall logs and visualize blocked IP addresses on a world map.

## Installation

```bash
pip3 install -e .
```

Or install dependencies manually:

```bash
pip3 install -r requirements.txt
```

## Usage

```bash
# Basic usage (scans ipt-example.log, outputs ip_map.png)
python3 -m ipview -i ipt-example.log

# Generate an interactive HTML map from ipt-example.log
python3 -m ipview -i ipt-example.log --html -o ip_map.html

# Create a symlink to analyze a log directory
ln -sfn /path/to/logs logdir
python3 -m ipview

# Specify input pattern and output file
python3 -m ipview -i "logdir/*" -o map.png

# Generate an interactive HTML map with zoom/pan (uses file modification time as timestamp)
python3 -m ipview -i "logdir/*" --html -o map.html

# Generate a density heatmap
python3 -m ipview -i "logdir/*" --heatmap -o heatmap.png

# Verbose mode
python3 -m ipview -i "logdir/*" -v

# Filter by minimum IP appearance frequency (default: 100)
python3 -m ipview -i "logdir/*" --min-freq 10
```

## IP Frequency Threshold

The `--min-freq` option filters IPs by their appearance frequency in log files. Only IPs appearing at least `min-freq` times will be included in the map. This helps focus on recurring threats rather than one-off attempts.

## Timestamps

When analyzing log directories, timestamps are extracted from the file modification time of each log file, allowing you to track when IPs were first seen over time.

## GeoIP Database

This tool requires the MaxMind GeoLite2 City database. Download it from:
https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

Set the path via environment variable or command line:

```bash
export GEOIP_DB_PATH=/path/to/GeoLite2-City.mmdb
python3 -m ipview --geo-db /path/to/GeoLite2-City.mmdb
```
