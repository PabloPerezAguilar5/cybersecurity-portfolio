#!/usr/bin/env python3
"""Send a test message or offline SSH detections to a private Telegram chat."""

import argparse
import getpass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import warnings
from urllib import error, request

from detect_ssh_failures import detect, parse_line


class TelegramError(Exception):
    """A safe error message that does not include the request URL or response."""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def telegram_call(token, method, payload):
    """Call a fixed Telegram endpoint without logging secrets or retrying sends."""
    if not re.fullmatch(r'\d+:[A-Za-z0-9_-]+', token):
        raise TelegramError('Invalid bot token format; check TELEGRAM_BOT_TOKEN.')
    if method not in ('sendMessage', 'getUpdates'):
        raise TelegramError('Unsupported Telegram operation.')
    url = f'https://api.telegram.org/bot{token}/{method}'
    req = request.Request(url, data=json.dumps(payload).encode('utf-8'),
                          headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=10) as response:
            data = json.load(response)
    except error.HTTPError as exc:
        raise TelegramError(f'Telegram returned HTTP {exc.code}; check credentials, chat and rate limits.') from None
    except (error.URLError, TimeoutError, OSError):
        raise TelegramError('Telegram connection failed or timed out; delivery may be unknown. Check network before retrying.') from None
    except (ValueError, UnicodeError):
        raise TelegramError('Telegram returned an invalid response; delivery may be unknown.') from None
    if not isinstance(data, dict) or data.get('ok') is not True:
        raise TelegramError('Telegram rejected the request; check credentials, chat and webhook configuration.')
    return data.get('result')


def config_path():
    return Path.home() / '.config' / 'soc-monitor' / 'credentials.json'


def validate_credentials(token, chat, require_chat=True):
    if not isinstance(token, str) or not re.fullmatch(r'\d+:[A-Za-z0-9_-]+', token):
        raise TelegramError('Invalid or missing bot token; run setup or set TELEGRAM_BOT_TOKEN.')
    if require_chat and (not isinstance(chat, str) or not re.fullmatch(r'-?\d+', chat)):
        raise TelegramError('Invalid or missing chat ID; run setup or set TELEGRAM_CHAT_ID.')


def hidden_token():
    # Refuse getpass fallback, which could echo the token on unsupported terminals.
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        return getpass.getpass('Telegram bot token (hidden): ').strip()


def setup():
    path = config_path()
    temporary = None
    try:
        exists = path.exists() or path.is_symlink()
        if exists and input('Credentials already exist. Replace them? [y/N]: ').strip().lower() != 'y':
            print('Existing credentials kept.')
            return
        token = hidden_token()
        chat = input('Private chat ID: ').strip()
        validate_credentials(token, chat)
        if path.parent.is_symlink() or path.is_symlink():
            raise TelegramError('Configuration must not use symbolic links.')
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        path.parent.chmod(0o700)
        fd, temporary = tempfile.mkstemp(prefix='.credentials-', dir=path.parent)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump({'token': token, 'chat_id': chat}, stream)
            stream.write('\n')
        if exists:
            os.replace(temporary, path)
        else:
            # Do not overwrite a file created while the prompts were open.
            os.link(temporary, path)
            os.unlink(temporary)
        temporary = None
        print('Telegram credentials saved. Run: python3 telegram_alerts.py test')
    except (EOFError, KeyboardInterrupt):
        raise TelegramError('Setup cancelled; credentials were not saved.') from None
    except getpass.GetPassWarning:
        raise TelegramError('Hidden input unavailable; run setup in an interactive terminal.') from None
    except OSError:
        raise TelegramError('Cannot save credentials; check configuration directory access.') from None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def credentials(require_chat=True):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat = os.environ.get('TELEGRAM_CHAT_ID')
    if token is None or (require_chat and chat is None):
        try:
            with config_path().open(encoding='utf-8') as stream:
                saved = json.load(stream)
            if not isinstance(saved, dict):
                raise ValueError
        except FileNotFoundError:
            saved = {}
        except (OSError, ValueError, UnicodeError):
            raise TelegramError('Cannot read saved credentials; run setup to repair configuration.') from None
        if token is None:
            token = saved.get('token')
        if chat is None:
            chat = saved.get('chat_id')
    validate_credentials(token, chat, require_chat)
    return token, chat


def format_detection(item, window_seconds, simulation):
    label = 'LAB / SIMULATION' if simulation else 'SSH AUTHENTICATION'
    return (f'{label}\nType: repeated SSH password failures\n'
            f'Source IP: {item.source}\nAttempts at threshold: {item.count}\n'
            f'Window: {window_seconds} seconds (inclusive)\n'
            f'First: {item.start.isoformat()}\nLast: {item.end.isoformat()}\n'
            'Indicative severity: medium (not validated)\n'
            'Requires investigation; this is not proof of an attack.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('setup', help='save Telegram credentials outside the repository')
    sub.add_parser('chat-id', help='list IDs of private chats in pending updates')
    sub.add_parser('test', help='send a LAB test notification')
    alerts = sub.add_parser('alert', help='analyze an offline file and send detections')
    alerts.add_argument('logfile', type=Path)
    alerts.add_argument('--threshold', type=int, default=3)
    alerts.add_argument('--window-seconds', type=int, default=60)
    mode = alerts.add_mutually_exclusive_group(required=True)
    mode.add_argument('--simulation', action='store_true', help='label output LAB / SIMULATION')
    mode.add_argument('--real', action='store_true', help='real event data; source IPs will be sent to Telegram')
    args = parser.parse_args(sys.argv[1:] or ['test'])
    if args.command == 'alert' and (args.threshold < 2 or args.window_seconds < 1):
        parser.error('threshold must be at least 2 and window must be positive')
    sent = 0
    attempted_send = False
    try:
        if args.command == 'setup':
            setup()
            return 0
        token, chat = credentials(require_chat=args.command != 'chat-id')
        if args.command == 'chat-id':
            updates = telegram_call(token, 'getUpdates', {'allowed_updates': ['message'], 'limit': 100})
            if not isinstance(updates, list):
                raise TelegramError('Unexpected Telegram response.')
            ids = set()
            for update in updates:
                if not isinstance(update, dict):
                    continue
                message = update.get('message')
                info = message.get('chat') if isinstance(message, dict) else None
                if isinstance(info, dict) and info.get('type') == 'private' and isinstance(info.get('id'), int):
                    ids.add(info['id'])
            if not ids:
                raise TelegramError('No private chat found. Send /start to the bot and check whether a webhook is active.')
            for chat_id in sorted(ids):
                print(f'Private chat ID: {chat_id}')
            return 0
        if args.command == 'test':
            telegram_call(token, 'sendMessage', {'chat_id': chat, 'text': 'LAB / SIMULATION\nSOC Monitor está funcionando. Mensaje de prueba.'})
            print('Telegram accepted the test message; check your phone.')
            return 0
        try:
            with args.logfile.open(encoding='utf-8') as stream:
                events = [event for line in stream if (event := parse_line(line)) is not None]
        except (OSError, UnicodeError):
            raise TelegramError('Cannot read the input file as UTF-8.') from None
        detections = detect(events, args.threshold, args.window_seconds)
        for item in detections:
            attempted_send = True
            telegram_call(token, 'sendMessage', {'chat_id': chat, 'text': format_detection(item, args.window_seconds, args.simulation)})
            sent += 1
        print(f'Matching failures: {len(events)}; messages accepted by Telegram: {len(detections)}')
        return 0
    except TelegramError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        if args.command == 'alert' and attempted_send:
            print(f'Confirmed messages before error: {sent}. Delivery of the failed request may be unknown; rerunning may duplicate messages.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
