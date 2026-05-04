"""Collect IP addresses from firewall log files."""

import re
import glob as glob_module
from typing import List, Set


def collect_dropped_ips(pattern: str) -> Set[str]:
    """Collect unique IP addresses from log files matching the pattern.

    Args:
        pattern: Glob pattern for log files (e.g., "*.log")

    Returns:
        Set of unique IP addresses found in DROP entries
    """
    ips: Set[str] = set()

    for filepath in glob_module.glob(pattern):
        try:
            with open(filepath, 'r', errors='ignore') as f:
                for line in f:
                    if 'DROP' in line:
                        ip = extract_ip(line)
                        if ip:
                            ips.add(ip)
        except IOError:
            continue

    return ips


def extract_ip(line: str) -> str | None:
    """Extract IP address from a log line.

    Args:
        line: A log line that may contain an IP address

    Returns:
        The first IP address found, or None if no IP found
    """
    # Match standard IPv4 address
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    match = re.search(ip_pattern, line)
    if match:
        ip = match.group()
        # Validate IP octets are in valid range
        octets = ip.split('.')
        if all(0 <= int(o) <= 255 for o in octets):
            return ip
    return None
