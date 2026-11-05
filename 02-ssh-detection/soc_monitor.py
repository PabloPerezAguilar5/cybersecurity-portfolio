#!/usr/bin/env python3
"""Follow new SSH journal entries and notify Telegram at the detection threshold."""

from datetime import timedelta
import subprocess
import sys

from detect_ssh_failures import detect, parse_line
from telegram_alerts import TelegramError, credentials, format_detection, telegram_call


JOURNAL_COMMAND = ['journalctl', '--no-pager', '--quiet', '--follow', '--lines=0',
                   '--unit=ssh.service', '--output=short-iso']


class Monitor:
    """Bounded-time windows with the existing detector's threshold/rearm semantics."""

    def __init__(self, send):
        self.send = send
        self.windows = {}
        self.active = set()
        self.latest = None

    def process(self, line):
        event = parse_line(line)
        if event is None:
            return
        # Arrival order is journal order; reject backward timestamps after clock changes.
        if self.latest is not None and event.timestamp < self.latest:
            return
        self.latest = event.timestamp
        cutoff = event.timestamp - timedelta(seconds=60)
        for source in list(self.windows):
            self.windows[source] = [item for item in self.windows[source]
                                    if item.timestamp >= cutoff]
            if not self.windows[source]:
                del self.windows[source]
                self.active.discard(source)
        events = self.windows.setdefault(event.source, [])
        if len(events) < 3:
            self.active.discard(event.source)
        events.append(event)
        if event.source not in self.active:
            results = detect(events, 3, 60)
            if results:
                self.active.add(event.source)
                self.send(results[-1])


def check_journal_access():
    try:
        result = subprocess.run(
            ['journalctl', '--no-pager', '--lines=1', '--unit=ssh.service',
             '--output=short-iso'], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        raise TelegramError('Cannot check journal access; verify journalctl is available.') from None
    if result.returncode != 0 or result.stderr.strip():
        raise TelegramError('Journal access check failed or reported a warning; verify SSH journal permissions.')
    if not any(parse_line(line) for line in result.stdout.splitlines()):
        print('No recent parseable SSH failure available; live event visibility remains unverified.')


def follow(monitor):
    process = None
    try:
        # Discard journal diagnostics to avoid exposing private identifiers.
        process = subprocess.Popen(JOURNAL_COMMAND, stdout=subprocess.PIPE,
                                   stderr=subprocess.DEVNULL, text=True,
                                   encoding='utf-8', errors='replace')
        print('Monitoring NEW SSH password failures (3 in 60 seconds). Ctrl+C to stop.', flush=True)
        for line in process.stdout:
            monitor.process(line)
        raise TelegramError('Journal stream ended; monitoring stopped. Check journal access before restarting.')
    except OSError:
        raise TelegramError('Cannot start or read journalctl.') from None
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            if process.stdout is not None:
                process.stdout.close()


def main():
    try:
        check_journal_access()
        token, chat = credentials()

        def send(item):
            telegram_call(token, 'sendMessage', {
                'chat_id': chat, 'text': format_detection(item, 60, False)})
            print('Telegram accepted an SSH detection; investigation required.', flush=True)

        follow(Monitor(send))
    except KeyboardInterrupt:
        print('\nMonitor stopped.')
        return 0
    except TelegramError as exc:
        print(f'Error: {exc}', file=sys.stderr)
        print('No automatic retry: delivery may be unknown. Restart begins with new events only.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
