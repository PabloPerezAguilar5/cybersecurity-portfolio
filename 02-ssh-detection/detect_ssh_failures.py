#!/usr/bin/env python3
"""Detect bursts of OpenSSH password failures in short-iso journal exports."""

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from ipaddress import ip_address
from pathlib import Path
import re
import sys


LINE = re.compile(
    r"^(?P<timestamp>\S+)\s+\S+\s+sshd\[\d+\]: "
    r"Failed password for (?:invalid user )?\S+ from "
    r"(?P<ip>\S+) port \d+ ssh2\s*$"
)


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    source: str


@dataclass(frozen=True)
class Detection:
    source: str
    start: datetime
    end: datetime
    count: int


def parse_line(line: str) -> Event | None:
    """Accept only timestamped OpenSSH Failed password entries with an IP."""
    match = LINE.match(line.strip())
    if not match:
        return None
    try:
        timestamp = datetime.fromisoformat(match['timestamp'])
        source = str(ip_address(match['ip']))
    except ValueError:
        return None
    if timestamp.utcoffset() is None:
        return None
    return Event(timestamp, source)


def detect(events: list[Event], threshold: int, window_seconds: int) -> list[Detection]:
    """Emit once when a source crosses the threshold in an inclusive window."""
    if threshold < 2 or window_seconds < 1:
        raise ValueError('threshold must be at least 2 and window must be positive')
    windows: dict[str, deque[datetime]] = defaultdict(deque)
    active: dict[str, bool] = defaultdict(bool)
    results = []
    window = timedelta(seconds=window_seconds)
    for event in sorted(events, key=lambda item: item.timestamp):
        times = windows[event.source]
        while times and event.timestamp - times[0] > window:
            times.popleft()
        if len(times) < threshold:
            active[event.source] = False
        times.append(event.timestamp)
        if len(times) >= threshold and not active[event.source]:
            results.append(Detection(event.source, times[0], event.timestamp, len(times)))
            active[event.source] = True
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('logfile', type=Path, help='UTF-8 journalctl -o short-iso export')
    parser.add_argument('--threshold', type=int, default=3, help='failures required (default: 3)')
    parser.add_argument('--window-seconds', type=int, default=60, help='inclusive window in seconds (default: 60)')
    args = parser.parse_args()
    if args.threshold < 2 or args.window_seconds < 1:
        parser.error('--threshold must be at least 2 and --window-seconds must be positive')
    try:
        with args.logfile.open(encoding='utf-8') as stream:
            lines = list(stream)
    except (OSError, UnicodeError) as exc:
        print(f'Cannot read input: {exc}', file=sys.stderr)
        return 2
    events = [event for line in lines if (event := parse_line(line)) is not None]
    detections = detect(events, args.threshold, args.window_seconds)
    print(f'Lines: {len(lines)}; matching failures: {len(events)}; ignored: {len(lines) - len(events)}')
    for result in detections:
        print(f'DETECTION source={result.source} count={result.count} '
              f'from={result.start.isoformat()} to={result.end.isoformat()}')
    print(f'Detections: {len(detections)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
