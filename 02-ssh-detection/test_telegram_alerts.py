import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib import error

import telegram_alerts as app


class TelegramTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.config = Path(temporary.name) / 'soc-monitor' / 'credentials.json'
        config_patch = patch.object(app, 'config_path', return_value=self.config)
        config_patch.start()
        self.addCleanup(config_patch.stop)
        self.env = patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '123:dummy_test', 'TELEGRAM_CHAT_ID': '12345'}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_successful_api_call(self):
        response = io.BytesIO(json.dumps({'ok': True, 'result': {'message_id': 4}}).encode())
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        with patch.object(app.request, 'build_opener', return_value=opener):
            result = app.telegram_call('123:dummy_test', 'sendMessage', {'chat_id': '12345', 'text': 'test'})
        self.assertEqual(result['message_id'], 4)
        sent = json.loads(opener.open.call_args.args[0].data)
        self.assertEqual(sent['text'], 'test')

    def test_rejection_does_not_echo_server_or_token(self):
        response = io.BytesIO(b'{"ok": false, "description": "123:dummy_test"}')
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        with patch.object(app.request, 'build_opener', return_value=opener):
            with self.assertRaises(app.TelegramError) as caught:
                app.telegram_call('123:dummy_test', 'sendMessage', {})
        self.assertNotIn('dummy_test', str(caught.exception))

    def test_network_and_http_errors_are_safe(self):
        for exc in (error.URLError('https://api.telegram.org/bot123:dummy_test'),
                    error.HTTPError('secret', 429, 'token', {}, None)):
            opener = MagicMock()
            opener.open.side_effect = exc
            with patch.object(app.request, 'build_opener', return_value=opener):
                with self.assertRaises(app.TelegramError) as caught:
                    app.telegram_call('123:dummy_test', 'sendMessage', {})
            self.assertNotIn('dummy_test', str(caught.exception))

    def test_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(sys.stdin, 'isatty', return_value=False):
            with self.assertRaises(app.TelegramError):
                app.credentials()

    def save_dummy(self):
        with patch.object(app.getpass, 'getpass', return_value='123:saved_dummy'), \
                patch('builtins.input', return_value='67890'), \
                contextlib.redirect_stdout(io.StringIO()):
            app.setup()

    def test_setup_permissions_and_saved_loading(self):
        self.save_dummy()
        self.assertEqual(self.config.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o600)
        with patch.dict(os.environ, {}, clear=True), \
                patch.object(app.getpass, 'getpass', side_effect=AssertionError), \
                patch('builtins.input', side_effect=AssertionError):
            self.assertEqual(app.credentials(), ('123:saved_dummy', '67890'))

    def test_environment_overrides_saved_values_individually(self):
        self.save_dummy()
        self.assertEqual(app.credentials(), ('123:dummy_test', '12345'))
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '123:override'}, clear=True):
            self.assertEqual(app.credentials(), ('123:override', '67890'))
        with patch.dict(os.environ, {'TELEGRAM_CHAT_ID': '999'}, clear=True):
            self.assertEqual(app.credentials(), ('123:saved_dummy', '999'))

    def test_existing_credentials_require_confirmation(self):
        self.save_dummy()
        before = self.config.read_bytes()
        with patch('builtins.input', return_value=''), \
                patch.object(app.getpass, 'getpass', side_effect=AssertionError), \
                contextlib.redirect_stdout(io.StringIO()):
            app.setup()
        self.assertEqual(self.config.read_bytes(), before)
        with patch('builtins.input', side_effect=['y', '222']), \
                patch.object(app.getpass, 'getpass', return_value='123:replacement'), \
                contextlib.redirect_stdout(io.StringIO()):
            app.setup()
        self.assertEqual(json.loads(self.config.read_text())['chat_id'], '222')
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o600)

    def test_cancelled_setup_preserves_file(self):
        self.save_dummy()
        before = self.config.read_bytes()
        with patch('builtins.input', return_value='y'), \
                patch.object(app.getpass, 'getpass', side_effect=EOFError):
            with self.assertRaisesRegex(app.TelegramError, 'cancelled'):
                app.setup()
        self.assertEqual(self.config.read_bytes(), before)

    def test_invalid_file_error_does_not_leak_contents(self):
        self.config.parent.mkdir()
        self.config.write_text('123:secret_dummy')
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(app.TelegramError) as caught:
                app.credentials()
        self.assertNotIn('secret_dummy', str(caught.exception))

    def test_saved_credentials_support_test_and_alert_without_prompts(self):
        self.save_dummy()
        sample = Path(__file__).parent / 'synthetic' / 'ssh-sample.txt'
        for arguments in (['test'], ['alert', str(sample), '--simulation']):
            with patch.dict(os.environ, {}, clear=True), \
                    patch.object(sys, 'argv', ['telegram_alerts.py'] + arguments), \
                    patch.object(app, 'telegram_call', return_value={}) as call, \
                    patch('builtins.input', side_effect=AssertionError), \
                    patch.object(app.getpass, 'getpass', side_effect=AssertionError), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(app.main(), 0)
            self.assertEqual(call.call_args.args[0], '123:saved_dummy')
            self.assertEqual(call.call_args.args[2]['chat_id'], '67890')

    def test_no_arguments_sends_test(self):
        with patch.object(sys, 'argv', ['telegram_alerts.py']), \
                patch.object(app, 'telegram_call', return_value={}) as call, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(), 0)
        self.assertEqual(call.call_args.args[1], 'sendMessage')

    def test_synthetic_file_sends_one_labeled_detection(self):
        sample = Path(__file__).parent / 'synthetic' / 'ssh-sample.txt'
        with patch.object(sys, 'argv', ['telegram_alerts.py', 'alert', str(sample), '--simulation']), \
                patch.object(app, 'telegram_call', return_value={}) as call, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(), 0)
        call.assert_called_once()
        message = call.call_args.args[2]['text']
        for expected in ('LAB / SIMULATION', '198.51.100.20', 'Attempts at threshold: 3', '60 seconds', 'Requires investigation'):
            self.assertIn(expected, message)

    def test_test_message(self):
        with patch.object(sys, 'argv', ['telegram_alerts.py', 'test']), \
                patch.object(app, 'telegram_call', return_value={}) as call, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(), 0)
        self.assertIn('SOC Monitor está funcionando', call.call_args.args[2]['text'])

    def test_below_threshold_sends_nothing(self):
        sample = Path(__file__).parent / 'synthetic' / 'ssh-sample.txt'
        with patch.object(sys, 'argv', ['telegram_alerts.py', 'alert', str(sample), '--simulation', '--threshold', '4']), \
                patch.object(app, 'telegram_call') as call, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(), 0)
        call.assert_not_called()

    def test_private_chat_ids_only(self):
        updates = [{'message': {'chat': {'type': 'private', 'id': 123}}},
                   {'message': {'chat': {'type': 'group', 'id': -456}}}]
        output = io.StringIO()
        with patch.object(sys, 'argv', ['telegram_alerts.py', 'chat-id']), \
                patch.object(app, 'telegram_call', return_value=updates), contextlib.redirect_stdout(output):
            self.assertEqual(app.main(), 0)
        self.assertIn('123', output.getvalue())
        self.assertNotIn('-456', output.getvalue())


if __name__ == '__main__':
    unittest.main()
