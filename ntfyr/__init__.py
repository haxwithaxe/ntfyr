"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""


from datetime import datetime as dt
import requests
import tzlocal

DEFAULT_SERVER = 'https://ntfy.sh'


class NtfyrError(Exception):
    """ntfyr flow control error

    Arguments:
        error (str): Message for the user.
        server (str, optional): The server name specified as an argument or in the config.
        topic (str, optional): The topic name specified as an argument or in the config.
        headers (dict, optional): The headers specified as an argument or in the config.
        message (str, optional): The message body specified as an argument or in the config.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, error, server=None, topic=None, message=None, headers=None):
        super().__init__(error)
        self.message = error
        self.server = server
        self.topic = topic
        self._message = message
        self.headers = headers


def _get_headers(args, config):
    """Get headers from arguments and configs."""
    headers = {}
    if args.actions or config.get('actions'):
        headers['Actions'] = args.actions or config.get('actions')
    if args.attach or config.get('attach'):
        headers['Attach'] = args.attach or config.get('attach')
    if args.click or config.get('click'):
        headers['Click'] = args.click or config.get('click')
    if args.delay or config.get('delay'):
        headers['Delay'] = args.delay or config.get('delay')
    if args.email or config.get('email'):
        headers['Email'] = args.email or config.get('email')
    if args.priority or config.get('priority'):
        headers['Priority'] = args.priority or config.get('priority')
    if config.get('tags'):
        headers['Tags'] = config.get('tags')
    if args.tags:  # Override default tags
        headers['Tags'] = ','.join(args.tags)
    if args.title or config.get('title'):
        headers['Title'] = args.title or config.get('title')
    return headers


def _get_timestamp(ts_format):
    """Returns the local time formatted with `ts_format`.

    See https://docs.python.org/3/library/time.html#time.strftime for string
    formatting options.
    """
    system_tz = tzlocal.get_localzone()
    now = dt.now(tz=system_tz)
    return now.strftime(ts_format)


def notify(args, config, message):
    """Send a notification.

    Arguments:
        args (argparse.Namespace): The arguments passed to the script.
        config (dict): Parsed config from the config file.
        message (str): The body of the message to be sent.
    """
    server = args.server or config.get('server', DEFAULT_SERVER)
    url = f'{server}/{args.topic}'
    headers = _get_headers(args, config)
    user = args.user or config.get('user', '')
    password = args.password or config.get('password', '')
    if user and password:
        credentials = (user, password)
    elif (user and not password) or (not user and password):
        raise NtfyrError('Either user or password was specified but not both.')
    else:
        credentials = None
    if args.timestamp or config.get('timestamp'):
        timestamp = args.timestamp or config.get('timestamp')
        if '%message' in timestamp:
            # Replacing % notation with {} to avoid confusion with strftime
            message_format = timestamp.replace('%message', '{message}')
            message = _get_timestamp(message_format).format(message=message)
        else:
            message = f'{_get_timestamp(timestamp)} {message}'
    res = requests.post(url=url, headers=headers, data=message.encode('utf-8'),
                        auth=credentials)
    if not res.ok:
        if res.json():
            raise NtfyrError('{error} {link}'.format(**res.json()), server,
                             args.topic, headers, message)
        raise NtfyrError(f'{res.status_code} {res.content.decode()}', server,
                         args.topic, headers, message)
