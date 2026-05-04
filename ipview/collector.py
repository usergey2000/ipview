"""Collect IP addresses from firewall log files."""

import re
import glob as glob_module
from typing import List, Set, Dict, Tuple
from datetime import datetime


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


def collect_dropped_ips_with_timestamp(pattern: str) -> Dict[str, datetime]:
    """Collect IPs with timestamps extracted from filenames.

    Args:
        pattern: Glob pattern for log files (e.g., "logdir/*.log")

    Returns:
        Dict mapping IPs to their earliest timestamp from log filenames
    """
    ip_timestamps: Dict[str, datetime] = {}

    for filepath in glob_module.glob(pattern):
        timestamp = extract_timestamp_from_filename(filepath)
        if timestamp is None:
            continue

        try:
            with open(filepath, 'r', errors='ignore') as f:
                for line in f:
                    if 'DROP' in line:
                        ip = extract_ip(line)
                        if ip:
                            # Keep the earliest timestamp for each IP
                            if ip not in ip_timestamps or timestamp < ip_timestamps[ip]:
                                ip_timestamps[ip] = timestamp
        except IOError:
            continue

    return ip_timestamps


def extract_timestamp_from_filename(filepath: str) -> datetime | None:
    """Extract timestamp from log filename.

    Expected filename formats:
    - iptables_Feb10_000001 -> 2026-02-10 00:00:01
    - iptables_Feb1_000001 -> 2026-02-01 00:00:01
    - iptables_Jan31_192501 -> 2026-01-31 19:25:01

    Args:
        filepath: Path to log file

    Returns:
        datetime object or None if no timestamp found
    """
    # Extract filename from path
    filename = filepath.split('/')[-1]

    # Match pattern: iptables_(Month)(Day)_(HHMMSS)
    # Month: Jan, Feb, Mar, etc.
    # Day: 1 or 2 digits (e.g., 1, 01, 31)
    # Time: 6 digits HHMMSS
    match = re.search(r'iptables_(\w+?)(\d{1,2})_(\d{6})$', filename)
    if not match:
        return None

    month_str, day_str, time_str = match.groups()

    # Parse month
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
        'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    month = month_map.get(month_str)
    if month is None:
        return None

    # Parse day and time
    day = int(day_str)
    hour = int(time_str[0:2])
    minute = int(time_str[2:4])
    second = int(time_str[4:6])

    # Use current year (2026) as log files don't include year
    year = 2026

    try:
        return datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


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
