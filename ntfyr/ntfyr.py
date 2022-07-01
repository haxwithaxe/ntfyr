"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""


from datetime import datetime as dt
import requests
import tzlocal

from .errors import NtfyrError


DEFAULT_SERVER = 'https://ntfy.sh'


def _get_headers(config):
    """Get headers from arguments and configs."""
    headers = {}
    if config.get('actions'):
        headers['Actions'] = config.get('actions')
    if config.get('attach'):
        headers['Attach'] = config.get('attach')
    if config.get('click'):
        headers['Click'] = config.get('click')
    if config.get('delay'):
        headers['Delay'] = config.get('delay')
    if config.get('email'):
        headers['Email'] = config.get('email')
    if config.get('priority'):
        headers['Priority'] = config.get('priority')
    if config.get('tags'):
        tags = config.get('tags')
        if isinstance(tags, (list, tuple)):
            tags = ','.join(tags)
        headers['Tags'] = tags
    if config.get('title'):
        headers['Title'] = config.get('title')
    return headers


def _get_timestamp(ts_format):
    """Returns the local time formatted with `ts_format`.

    See https://docs.python.org/3/library/time.html#time.strftime for string
    formatting options.
    """
    system_tz = tzlocal.get_localzone()
    now = dt.now(tz=system_tz)
    return now.strftime(ts_format)


def notify(config, message):
    """Send a notification.

    Arguments:
        args (argparse.Namespace): The arguments passed to the script.
        config (dict): Parsed config from the config file.
        message (str): The body of the message to be sent.
    """
    server = config.get('server', DEFAULT_SERVER)
    url = f'{server}/{config.get("topic")}'
    headers = _get_headers(config)
    user = config.get('user', '')
    password = config.get('password', '')
    if user and password:
        credentials = (user, password)
    elif (user and not password) or (not user and password):
        raise NtfyrError('Either user or password was specified but not both.')
    else:
        credentials = None
    if config.get('timestamp'):
        timestamp = config.get('timestamp')
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
                             config.get('topic'), headers, message)
        raise NtfyrError(f'{res.status_code} {res.content.decode()}', server,
                         config.get('topic'), headers, message)
