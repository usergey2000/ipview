"""Generate world map visualization from IP geolocation data."""

import os
from typing import Dict
from collections import defaultdict
import json
from datetime import datetime

try:
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np
except ImportError:
    ccrs = None
    plt = None
    np = None


def create_world_map(
    ip_locations: Dict[str, Dict[str, float]],
    output_path: str = 'ip_map.png',
    title: str = 'Blocked IP Locations'
) -> str:
    """Create a world map with points at IP locations.

    Args:
        ip_locations: Dict mapping IPs to location info (lat, lon, country, city)
        output_path: Path to save the output image
        title: Map title

    Returns:
        Path to the saved image
    """
    if plt is None or ccrs is None:
        raise RuntimeError("matplotlib and cartopy are required for map generation")

    # Separate coordinates
    lats = [loc['lat'] for loc in ip_locations.values()]
    lons = [loc['lon'] for loc in ip_locations.values()]

    # Create the map with PlateCarree projection (lat/lon)
    plt.figure(figsize=(14, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add coastlines and borders
    ax.coastlines(linewidth=0.5, color='gray')
    ax.stock_img()

    # Plot IP locations
    ax.scatter(
        lons, lats,
        c='red',
        s=30,
        alpha=0.7,
        transform=ccrs.PlateCarree(),
        edgecolors='darkred',
        linewidths=0.5
    )

    ax.set_global()
    ax.set_title(title, fontsize=14, pad=20)

    # Save the figure
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    return output_path


def create_heatmap(
    ip_locations: Dict[str, Dict[str, float]],
    output_path: str = 'ip_heatmap.png',
    title: str = 'IP Density Heatmap'
) -> str:
    """Create a density heatmap of IP locations.

    Args:
        ip_locations: Dict mapping IPs to location info
        output_path: Path to save the output image
        title: Map title

    Returns:
        Path to the saved image
    """
    if plt is None or ccrs is None:
        raise RuntimeError("matplotlib and cartopy are required for map generation")

    lats = [loc['lat'] for loc in ip_locations.values()]
    lons = [loc['lon'] for loc in ip_locations.values()]

    # Create 2D histogram data
    heatmap_data, xedges, yedges = np.histogram2d(
        lons, lats,
        bins=[72, 36],
        range=[[-180, 180], [-90, 90]]
    )

    # Create custom colormap
    colors = [(0, 0, 1, 0), (0, 1, 1, 0.5), (0, 1, 0, 0.7), (1, 0, 0, 1)]
    cmap = LinearSegmentedColormap.from_list('heat', colors)

    # Create the map with PlateCarree projection
    plt.figure(figsize=(14, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add coastlines
    ax.coastlines(linewidth=0.5, color='white')
    ax.stock_img()

    # Plot heatmap
    img = ax.imshow(
        heatmap_data.T,
        extent=[-180, 180, -90, 90],
        origin='lower',
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        alpha=0.6
    )

    ax.set_global()
    ax.set_title(title, fontsize=14, pad=20)

    plt.colorbar(img, label='Blocked IP Count', pad=0.02, ax=ax)

    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    return output_path


def create_interactive_map(
    ip_locations: Dict[str, Dict[str, float]],
    output_path: str = 'ip_map.html',
    title: str = 'Blocked IP Locations',
    ip_timestamps: Dict[str, datetime] | None = None,
    ip_frequencies: Dict[str, int] | None = None
) -> str:
    """Create an interactive HTML map with zoomable IP locations using Leaflet.js.

    Args:
        ip_locations: Dict mapping IPs to location info (lat, lon, country, city)
        output_path: Path to save the HTML output
        title: Map title
        ip_timestamps: Optional dict mapping IPs to their timestamps
        ip_frequencies: Optional dict mapping IPs to their occurrence counts

    Returns:
        Path to the saved HTML file
    """
    # Separate coordinates and build IP data
    lats = [loc.get('lat', 0) for loc in ip_locations.values()]
    lons = [loc.get('lon', 0) for loc in ip_locations.values()]

    # Calculate map center (average lat/lon)
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Build marker HTML
    markers = []
    for ip, loc in ip_locations.items():
        country = loc.get('country', 'Unknown')
        city = loc.get('city', 'Unknown')
        lat = loc.get('lat', 0)
        lon = loc.get('lon', 0)

        # Include timestamp if available
        timestamp_info = ""
        if ip_timestamps and ip in ip_timestamps:
            ts = ip_timestamps[ip]
            timestamp_info = f"<br><b>Timestamp:</b> {ts.strftime('%Y-%m-%d %H:%M:%S')}"

        # Include frequency if available
        frequency_info = ""
        if ip_frequencies and ip in ip_frequencies:
            count = ip_frequencies[ip]
            frequency_info = f"<br><b>Count:</b> {count} occurrence{'s' if count > 1 else ''}"

        marker_html = f"""        L.marker([{lat}, {lon}])
            .addTo(map)
            .bindPopup("<b>{ip}</b><br>{country}{', ' + city if city else ''}{timestamp_info}{frequency_info}");"""
        markers.append(marker_html)

    markers_html = "\n".join(markers)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossorigin=""/>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #map {{
            height: 100vh;
            width: 100%;
        }}
        .leaflet-popup-content {{
            margin: 0;
            line-height: 1.5;
        }}
        .leaflet-popup-content-wrapper {{
            background-color: #fff;
            color: #333;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
            crossorigin=""></script>
    <script>
        // Initialize map centered on the IP locations
        var map = L.map('map').setView([{center_lat}, {center_lon}], 2);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
            noWrap: false
        }}).addTo(map);

        // Add markers for each IP location
{markers_html}
    </script>
</body>
</html>"""

    with open(output_path, 'w') as f:
        f.write(html_content)

    return output_path
