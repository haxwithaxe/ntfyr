"""A script to send notifications to https://ntfy.sh

This script is a part of the python package ntfyr which can be found at
https://github.com/haxwithaxe/ntfyr and https://pypi.org/project/ntfyr/
"""


import argparse
import logging
import select
import sys

from .config import Config
from .errors import NtfyrError
from .ntfyr import Ntfyr
from ._common import log


DEFAULT_TIMESTAMP = '%Y-%m-%d %H:%M:%S %Z'
PRIORITIES = ['max', 'urgent', 'high', 'default', 'low', 'min', '1', '2', '3',
              '4', '5']


def main(): # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser(description='Send a notification with ntfy.')
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
                        help='The password to authenticate to the server with.')
    parser.add_argument(
        '-c',
        '--config',
        default=None,
        help='The configuration file with default values.'
             ' The values specified as arguments override the'
             ' values in this file.'
    )
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Show extra information in the error messages.')
    args = parser.parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)
    if args.config:
        config = Config(args, args.config, '/etc/ntfyr/config.ini')
    else:
        config = Config(args, '/etc/ntfyr/config.ini')
    if args.message == '-':
        if select.select([sys.stdin], [], [], 0)[0]:
            message = sys.stdin.read()
        else:
            log.warning('--message is empty and there is no stdin. Sending an '
                        'empty message.')
            message = ''
    else:
        message = args.message
    try:
        Ntfyr(config).notify(message)
    except NtfyrError as err:
        print(f'Error sending to {err.server}/{err.topic}: {err.message}',
              file=sys.stderr)
        if args.debug:
            print('Sent headers:', err.headers, file=sys.stderr)
            print(f'Sent message:\n{message}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as err: # pylint: disable=broad-except
        print(err, file=sys.stderr)
        sys.exit(2)
