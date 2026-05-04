#!/usr/bin/env python3
"""Main entry point for ipview."""

import argparse
import sys
from typing import List

from .collector import collect_dropped_ips, collect_dropped_ips_with_stats, filter_timestamps_by_date
from .geo import get_geo_locations, GeoIPLookup
from .map import create_world_map, create_heatmap, create_interactive_map


def main(args: List[str] = None) -> int:
    """Run the ipview tool."""
    parser = argparse.ArgumentParser(
        description='Analyze firewall logs and visualize blocked IPs on a world map'
    )
    parser.add_argument(
        '-i', '--input',
        default='*.log',
        help='Glob pattern for log files (default: *.log)'
    )
    parser.add_argument(
        '-o', '--output',
        default='ip_map.png',
        help='Output path for the world map (default: ip_map.png)'
    )
    parser.add_argument(
        '--heatmap',
        action='store_true',
        help='Generate a density heatmap instead of point map'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate an interactive HTML map with zoom/pan capability'
    )
    parser.add_argument(
        '--geo-db',
        help='Path to GeoLite2 City database'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--start-date',
        help='Start date in MM-DD-YYYY format (inclusive)'
    )
    parser.add_argument(
        '--end-date',
        help='End date in MM-DD-YYYY format (inclusive)'
    )

    parsed = parser.parse_args(args)

    # Collect IPs from logs
    if parsed.verbose:
        print(f"Scanning for log files matching: {parsed.input}")

    ip_timestamps = None

    # Collect IPs and get timestamps from file modification time
    ip_timestamps, ip_frequencies = collect_dropped_ips_with_stats(parsed.input)

    # Filter by date range if specified
    ip_timestamps = filter_timestamps_by_date(
        ip_timestamps,
        parsed.start_date,
        parsed.end_date
    )
    # Also filter frequencies to match
    if ip_frequencies:
        ip_frequencies = {ip: count for ip, count in ip_frequencies.items() if ip in ip_timestamps}

    ips = set(ip_timestamps.keys())

    if not ips:
        print("No IPs with DROP entries found.", file=sys.stderr)
        return 1

    if parsed.verbose:
        print(f"Found {len(ips)} unique IP(s) with DROP entries")
        print("Timestamps from file modification times:")
        print(f"Frequency range: {min(ip_frequencies.values()) if ip_frequencies else 0} - {max(ip_frequencies.values()) if ip_frequencies else 0}")
        for ip, ts in sorted(ip_timestamps.items())[:5]:
            print(f"  {ip}: {ts}")
        if len(ip_timestamps) > 5:
            print(f"  ... and {len(ip_timestamps) - 5} more")

    # Geolocate IPs
    if parsed.verbose:
        print("Looking up geographic locations...")

    geo = GeoIPLookup(database_path=parsed.geo_db)
    try:
        locations = geo.batch_lookup(list(ips))
    finally:
        geo.close()

    # Filter out IPs that couldn't be geolocated (None lat/lon)
    valid_locations = {ip: loc for ip, loc in locations.items() if loc.get('lat') is not None}

    if not valid_locations:
        print("No geographic locations found for any IPs.", file=sys.stderr)
        return 1

    if parsed.verbose:
        if len(valid_locations) < len(locations):
            print(f"Filtered {len(locations) - len(valid_locations)} IP(s) without valid location")

    if parsed.verbose:
        print(f"Geolocated {len(valid_locations)} IP(s)")
        for ip, loc in valid_locations.items():
            city = loc.get('city')
            city_str = f", {city}" if city else ""
            lat = loc.get('lat', 0)
            lon = loc.get('lon', 0)
            print(f"  {ip}: {loc['country']}{city_str} ({lat:.4f}, {lon:.4f})")

    # Generate map
    output_path = parsed.output
    if parsed.heatmap:
        output_path = create_heatmap(valid_locations, output_path)
    elif parsed.html:
        output_path = create_interactive_map(valid_locations, output_path, ip_timestamps=ip_timestamps, ip_frequencies=ip_frequencies)
    else:
        output_path = create_world_map(valid_locations, output_path)

    print(f"Map saved to: {output_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
