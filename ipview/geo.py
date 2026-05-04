"""Geolocate IP addresses using MaxMind GeoIP database."""

import os
from typing import Dict, List, Tuple
from geoip2 import database
from geoip2.errors import AddressNotFoundError


class GeoIPLookup:
    """Wrapper for GeoIP database lookups."""

    def __init__(self, database_path: str = None):
        """Initialize the GeoIP database reader.

        Args:
            database_path: Path to MaxMind GeoLite2 City database.
                          Uses environment variable or default location.
        """
        if database_path is None:
            database_path = os.environ.get('GEOIP_DB_PATH', '/usr/share/GeoIP/GeoLite2-City.mmdb')

        self.reader = None
        if os.path.exists(database_path):
            try:
                self.reader = database.Reader(database_path)
            except Exception:
                pass

    def get_location(self, ip: str) -> Dict[str, float] | None:
        """Get location coordinates for an IP address.

        Args:
            ip: IP address to look up

        Returns:
            Dict with 'lat' and 'lon' keys, or None if not found
        """
        if self.reader is None:
            return None

        try:
            response = self.reader.city(ip)
            if response and response.location:
                return {
                    'lat': response.location.latitude,
                    'lon': response.location.longitude,
                    'country': response.country.name,
                    'city': response.city.name
                }
        except AddressNotFoundError:
            pass
        except Exception:
            pass

        return None

    def batch_lookup(self, ips: List[str]) -> Dict[str, Dict[str, float]]:
        """Look up locations for multiple IPs.

        Args:
            ips: List of IP addresses

        Returns:
            Dict mapping IPs to location dicts
        """
        results = {}
        for ip in ips:
            loc = self.get_location(ip)
            if loc:
                results[ip] = loc
        return results

    def close(self):
        """Close the database reader."""
        if self.reader:
            self.reader.close()


def get_geo_locations(ips: List[str]) -> Dict[str, Tuple[float, float]]:
    """Convenience function to get latitude/longitude for IPs.

    Args:
        ips: List of IP addresses

    Returns:
        Dict mapping IPs to (lat, lon) tuples
    """
    geo = GeoIPLookup()
    try:
        results = geo.batch_lookup(ips)
        return {ip: (loc['lat'], loc['lon']) for ip, loc in results.items()}
    finally:
        geo.close()
