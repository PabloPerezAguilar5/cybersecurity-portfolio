#!/usr/bin/env python3
"""Detached runner with an exclusive lock and private, rotating operational logs."""

import contextlib
import fcntl
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import signal
import sys

import soc_monitor


class LogStream:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, text):
        if text.strip():
            self.logger.log(self.level, text.strip())

    def flush(self):
        pass


def stop(signum, frame):
    raise KeyboardInterrupt


def run():
    os.umask(0o077)
    state = Path.home() / '.local' / 'state' / 'soc-monitor'
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    state.chmod(0o700)
    with (state / 'monitor.lock').open('a+') as lock:
        os.fchmod(lock.fileno(), 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Monitor already running.', file=sys.stderr)
            return 1
        lock.seek(0)
        lock.truncate()
        lock.write(str(os.getpid()) + '\n')
        lock.flush()
        handler = RotatingFileHandler(state / 'monitor.log', maxBytes=262144,
                                      backupCount=2, encoding='utf-8')
        os.chmod(state / 'monitor.log', 0o600)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger = logging.getLogger('soc-monitor')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        logger.info('Monitor starting; PID %s', os.getpid())
        try:
            with contextlib.redirect_stdout(LogStream(logger, logging.INFO)), \
                    contextlib.redirect_stderr(LogStream(logger, logging.ERROR)):
                try:
                    return soc_monitor.main()
                except Exception:
                    # Never log arbitrary exception strings or tracebacks containing secrets.
                    logger.error('Unexpected monitor failure; stopped without retry. No exception details logged.')
                    return 1
        finally:
            logger.info('Monitor exited.')
            logger.removeHandler(handler)
            handler.close()


if __name__ == '__main__':
    raise SystemExit(run())
