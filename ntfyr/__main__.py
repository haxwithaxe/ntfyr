"""A script to send notifications to [ntfy.sh](https://ntfy.sh).

This script is a part of the python package ntfyr which can be found at
https://github.com/haxwithaxe/ntfyr and https://pypi.org/project/ntfyr/
"""


import argparse
import logging
import select
import sys

from ._common import log
from .config import Config, DEFAULT_TIMESTAMP, PRIORITIES
from .errors import NtfyrError
from .ntfyr import notify


def _parse_args(args):
    parser = argparse.ArgumentParser(
        description='Send a notification with ntfy.'
    )
    # Headers
    parser.add_argument('-A', '--actions', default=None,
                        help='See https://ntfy.sh/docs/publish/')
    parser.add_argument('-X', '--attach', default=None,
                        help='See https://ntfy.sh/docs/publish/')
    parser.add_argument('-C', '--click', default=None,
                        help='See https://ntfy.sh/docs/publish/')
    parser.add_argument('-D', '--delay', default=None,
                        help='See https://ntfy.sh/docs/publish/')
    parser.add_argument('-E', '--email', default=None,
                        help='See https://ntfy.sh/docs/publish/')
    parser.add_argument('-P', '--priority', choices=PRIORITIES,
                        default='default',
                        help='See https://ntfy.sh/docs/publish/')
    parser.add_argument('-G', '--tags', nargs='+', default=[],
                        help='See https://ntfy.sh/docs/publish/')
    parser.add_argument('-T', '--title', default=None,
                        help='See https://ntfy.sh/docs/publish/')
    # Data
    parser.add_argument('-m', '--message', default='-',
                        help='The body of the message to send. The default'
                             ' (or if "-" is given) is to read from stdin.')
    parser.add_argument(
        '--timestamp',
        nargs='?',
        const=DEFAULT_TIMESTAMP,
        default=None,
        help='A time format string to prefix the message. See '
             'https://docs.python.org/3/library/time.html#time.strftime for '
             'formatting options.'
    )
    # Config
    parser.add_argument('-t', '--topic', required=True,
                        help='The topic to send the notification to. Required')
    parser.add_argument('-s', '--server', default=None,
                        help='The server to send the notification to.')
    parser.add_argument('-u', '--user', default=None,
                        help='The user to authenticate to the server with.')
    parser.add_argument('-p', '--password', default=None,
                        help='The password to authenticate to the server with.'
                        )
    parser.add_argument(
        '-c',
        '--config',
        default=None,
        help='The configuration file with default values.'
             ' The values specified as arguments override the'
             ' values in this file.'
    )
    parser.add_argument(
        '--log-level',
        default='ERROR',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the log level.'
    )
    return parser.parse_args(args)


def _configure(args):
    # Setup logging
    if args.log_level:
        log.setLevel(getattr(logging, args.log_level.upper()))
    # Assemble the config
    return Config.from_args(args)


def _get_message(args):
    if args.message == '-':
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read()
        else:
            return ''
    else:
        return args.message


def main():  # noqa: D103
    args = _parse_args(sys.argv)
    config = _configure(args)
    message = _get_message(args)
    try:
        notify(config, message)
    except NtfyrError as err:
        log.error('Error sending to {err.server}/{err.topic}: '
                  '{err.__class__.__name__}: {err.message}',
                  err=err)
        log.debug('Sent headers: %s', err.headers)
        log.debug('Sent message:\n%s', message)
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print('ERROR:ntfyr:', err.__class__.__name__, err, file=sys.stderr)
        sys.exit(2)
