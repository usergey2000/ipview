"""Collect IP addresses from firewall log files."""

import os
import re
import glob as glob_module
from typing import List, Set, Dict, Tuple
from datetime import datetime
from collections import defaultdict


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


def collect_dropped_ips_with_stats(pattern: str) -> Tuple[Dict[str, datetime], Dict[str, int]]:
    """Collect IPs with timestamps and frequency counts from file modification time.

    Args:
        pattern: Glob pattern for log files (e.g., "logdir/*")

    Returns:
        Tuple of (ip_timestamps, ip_frequencies)
        - ip_timestamps: Dict mapping IPs to their file's modification timestamp
        - ip_frequencies: Dict mapping IPs to their occurrence count
    """
    ip_timestamps: Dict[str, datetime] = {}
    ip_frequencies: Dict[str, int] = defaultdict(int)

    for filepath in glob_module.glob(pattern):
        # Skip if not a regular file
        if not os.path.isfile(filepath):
            continue

        # Get file modification time
        try:
            mtime = os.path.getmtime(filepath)
            timestamp = datetime.fromtimestamp(mtime)
        except OSError:
            continue

        try:
            with open(filepath, 'r', errors='ignore') as f:
                for line in f:
                    if 'DROP' in line:
                        ip = extract_ip(line)
                        if ip:
                            ip_frequencies[ip] += 1
                            # Keep the earliest timestamp for each IP
                            if ip not in ip_timestamps or timestamp < ip_timestamps[ip]:
                                ip_timestamps[ip] = timestamp
        except IOError:
            continue

    return ip_timestamps, dict(ip_frequencies)


def filter_timestamps_by_date(
    ip_timestamps: Dict[str, datetime],
    start_date: str | None,
    end_date: str | None
) -> Dict[str, datetime]:
    """Filter IP timestamps by date range.

    Args:
        ip_timestamps: Dict mapping IPs to timestamps
        start_date: Start date in MM-DD-YYYY format (inclusive)
        end_date: End date in MM-DD-YYYY format (inclusive)

    Returns:
        Filtered dict with IPs in the date range
    """
    if start_date is None and end_date is None:
        return ip_timestamps

    # Parse start_date
    start_dt = None
    if start_date:
        parts = start_date.split('-')
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        start_dt = datetime(year, month, day)

    # Parse end_date
    end_dt = None
    if end_date:
        parts = end_date.split('-')
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        end_dt = datetime(year, month, day)

    result = {}
    for ip, ts in ip_timestamps.items():
        # Compare only dates (ignore time component)
        ts_date = datetime(ts.year, ts.month, ts.day)

        if start_dt and ts_date < start_dt:
            continue
        if end_dt and ts_date > end_dt:
            continue
        result[ip] = ts

    return result


def filter_by_frequency(
    ip_frequencies: Dict[str, int],
    min_count: int | None = None,
    max_count: int | None = None
) -> Dict[str, int]:
    """Filter IPs by frequency count.

    Args:
        ip_frequencies: Dict mapping IPs to occurrence counts
        min_count: Minimum occurrence count (inclusive)
        max_count: Maximum occurrence count (inclusive)

    Returns:
        Filtered dict with IPs matching frequency criteria
    """
    result = ip_frequencies.copy()

    if min_count is not None:
        result = {ip: count for ip, count in result.items() if count >= min_count}
    if max_count is not None:
        result = {ip: count for ip, count in result.items() if count <= max_count}

    return result


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
