import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import soc_monitor_background as runner


class BackgroundTests(unittest.TestCase):
    def test_private_logs_and_safe_unexpected_error(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(runner.Path, 'home', return_value=Path(temporary)), \
                patch.object(runner.signal, 'signal'), \
                patch.object(runner.soc_monitor, 'main', side_effect=ValueError('dummy-secret')):
            old_mask = runner.os.umask(0o077)
            try:
                self.assertEqual(runner.run(), 1)
            finally:
                runner.os.umask(old_mask)
            state = Path(temporary) / '.local/state/soc-monitor'
            self.assertEqual(state.stat().st_mode & 0o777, 0o700)
            self.assertEqual((state / 'monitor.log').stat().st_mode & 0o777, 0o600)
            self.assertNotIn('dummy-secret', (state / 'monitor.log').read_text())

    def test_duplicate_runner_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(runner.Path, 'home', return_value=Path(temporary)), \
                patch.object(runner.fcntl, 'flock', side_effect=BlockingIOError), \
                patch.object(runner.soc_monitor, 'main') as main, \
                contextlib.redirect_stderr(io.StringIO()):
            old_mask = runner.os.umask(0o077)
            try:
                self.assertEqual(runner.run(), 1)
            finally:
                runner.os.umask(old_mask)
            main.assert_not_called()
