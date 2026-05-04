#!/usr/bin/env python3
"""Main entry point for ipview."""

import argparse
import sys
from typing import List

from .collector import collect_dropped_ips
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

    parsed = parser.parse_args(args)

    # Collect IPs from logs
    if parsed.verbose:
        print(f"Scanning for log files matching: {parsed.input}")

    ips = collect_dropped_ips(parsed.input)

    if not ips:
        print("No IPs with DROP entries found.", file=sys.stderr)
        return 1

    if parsed.verbose:
        print(f"Found {len(ips)} unique IP(s) with DROP entries")

    # Geolocate IPs
    if parsed.verbose:
        print("Looking up geographic locations...")

    geo = GeoIPLookup(database_path=parsed.geo_db)
    try:
        locations = geo.batch_lookup(list(ips))
    finally:
        geo.close()

    if not locations:
        print("No geographic locations found for any IPs.", file=sys.stderr)
        return 1

    if parsed.verbose:
        print(f"Geolocated {len(locations)} IP(s)")
        for ip, loc in locations.items():
            print(f"  {ip}: {loc['country']}, {loc['city']} ({loc['lat']:.4f}, {loc['lon']:.4f})")

    # Generate map
    output_path = parsed.output
    if parsed.heatmap:
        output_path = create_heatmap(locations, output_path)
    elif parsed.html:
        output_path = create_interactive_map(locations, output_path)
    else:
        output_path = create_world_map(locations, output_path)

    print(f"Map saved to: {output_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
