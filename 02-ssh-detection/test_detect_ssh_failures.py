import unittest
from datetime import datetime

from detect_ssh_failures import Event, detect, parse_line


def event(second, source='192.0.2.1'):
    return Event(datetime.fromisoformat(f'2026-11-04T18:{second // 60:02}:{second % 60:02}-03:00'), source)


class DetectionTests(unittest.TestCase):
    def test_below_threshold(self):
        self.assertEqual(detect([event(0), event(30)], 3, 60), [])

    def test_boundary_and_out_of_order(self):
        results = detect([event(60), event(0), event(30)], 3, 60)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].count, 3)
        self.assertEqual((results[0].end - results[0].start).total_seconds(), 60)
        # Different offsets still represent instants on the same timeline.
        different_zone = Event(datetime.fromisoformat('2026-11-04T21:00:30+00:00'), '192.0.2.1')
        results = detect([event(60), different_zone, event(0)], 3, 60)
        self.assertEqual(len(results), 1)
        self.assertEqual((results[0].end - results[0].start).total_seconds(), 60)

    def test_outside_window_and_separate_sources(self):
        self.assertEqual(detect([event(0), event(30), event(61)], 3, 60), [])
        self.assertEqual(detect([event(0), event(1, '192.0.2.2'), event(2)], 3, 60), [])

    def test_one_alert_per_burst_then_rearm(self):
        results = detect([event(n) for n in (0, 1, 2, 3, 100, 101, 102)], 3, 60)
        self.assertEqual(len(results), 2)
        # Duplicate input is counted, not deduplicated; it can reach the threshold.
        duplicate = event(0)
        results = detect([duplicate, duplicate, duplicate], 3, 60)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].count, 3)

    def test_parser_handles_invalid_user_and_ipv6(self):
        line = '2026-11-04T18:05:00-03:00 host sshd[7]: Failed password for invalid user demo from 2001:db8::1 port 42 ssh2'
        self.assertEqual(parse_line(line).source, '2001:db8::1')

    def test_parser_rejects_unrelated_and_invalid(self):
        self.assertIsNone(parse_line('2026-11-04T18:05:00-03:00 host sshd[7]: Accepted publickey for demo from 192.0.2.1 port 42 ssh2'))
        self.assertIsNone(parse_line('2026-11-04T18:05:00-03:00 host sshd[7]: Failed password for demo from 999.1.1.1 port 42 ssh2'))
        self.assertIsNone(parse_line('2026-11-04T18:05:00 host sshd[7]: Failed password for demo from 192.0.2.1 port 42 ssh2'))

    def test_invalid_settings(self):
        with self.assertRaises(ValueError):
            detect([], 1, 60)
        with self.assertRaises(ValueError):
            detect([], 3, 0)


if __name__ == '__main__':
    unittest.main()
