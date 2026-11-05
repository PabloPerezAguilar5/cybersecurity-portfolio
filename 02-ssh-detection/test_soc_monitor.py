import contextlib
from datetime import datetime, timedelta
import io
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from detect_ssh_failures import detect, parse_line
import soc_monitor as app


def line(second, ip='192.0.2.1'):
    stamp = datetime.fromisoformat('2026-11-04T18:00:00+00:00') + timedelta(seconds=second)
    return f'{stamp.isoformat()} lab sshd[7]: Failed password for demo from {ip} port 42 ssh2'


class MonitorTests(unittest.TestCase):
    def test_matches_offline_rule_and_rearms(self):
        for seconds in ((0, 30), (0, 30, 60), (0, 30, 61),
                        (0, 1, 2, 3, 100, 101, 102), (0, 30, 60, 61, 62, 63)):
            with self.subTest(seconds=seconds):
                send = MagicMock()
                monitor = app.Monitor(send)
                lines = [line(second) for second in seconds]
                for value in lines:
                    monitor.process(value)
                self.assertEqual([call.args[0] for call in send.call_args_list],
                                 detect([parse_line(value) for value in lines], 3, 60))

    def test_sources_and_ignored_lines(self):
        send = MagicMock()
        monitor = app.Monitor(send)
        for value in (line(0), line(1, '2001:db8::1'), 'unrelated', line(2)):
            monitor.process(value)
        send.assert_not_called()
        monitor.process(line(3))
        send.assert_called_once()
        monitor.process(line(4))
        send.assert_called_once()
        monitor.process(line(100, '192.0.2.2'))
        self.assertNotIn('192.0.2.1', monitor.windows)

    def test_backward_clock_is_ignored(self):
        send = MagicMock()
        monitor = app.Monitor(send)
        for second in (10, 9, 11):
            monitor.process(line(second))
        send.assert_not_called()

    def test_access_warning_fails_without_showing_logs(self):
        result = subprocess.CompletedProcess([], 0, 'private log', 'permission warning')
        with patch.object(app.subprocess, 'run', return_value=result):
            with self.assertRaises(app.TelegramError):
                app.check_journal_access()

    def test_follow_uses_new_entries_and_cleans_up_on_interrupt(self):
        process = MagicMock()
        process.stdout = io.StringIO(line(0))
        process.poll.return_value = None
        monitor = MagicMock()
        monitor.process.side_effect = KeyboardInterrupt
        with patch.object(app.subprocess, 'Popen', return_value=process) as popen, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                app.follow(monitor)
        self.assertIn('--lines=0', popen.call_args.args[0])
        self.assertIn('--follow', popen.call_args.args[0])
        process.terminate.assert_called_once()
        process.wait.assert_called_once()
        self.assertTrue(process.stdout.closed)

    def test_send_error_stops_without_retry(self):
        with patch.object(app, 'check_journal_access'), \
                patch.object(app, 'credentials', return_value=('123:dummy', '12345')), \
                patch.object(app, 'telegram_call', side_effect=app.TelegramError('failed')) as send, \
                patch.object(app, 'follow', side_effect=lambda monitor: [monitor.process(line(n)) for n in range(4)]), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(app.main(), 1)
        send.assert_called_once()


if __name__ == '__main__':
    unittest.main()
