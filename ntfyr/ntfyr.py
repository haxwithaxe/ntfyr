"""The main `ntfyr` functionality."""


import json
from datetime import datetime as dt

import requests
import tzlocal

from ._common import log
from .errors import NtfyrError


def _get_headers(config):
    """Get headers from arguments and configs."""
    headers = {}
    if config.token:
        headers['Authorization'] = f'Bearer {config.token}'
    if config.actions:
        headers['Actions'] = config.actions
    if config.attach:
        headers['Attach'] = config.attach
    if config.click:
        headers['Click'] = config.click
    if config.delay:
        headers['Delay'] = config.delay
    if config.email:
        headers['Email'] = config.email
    if config.priority:
        headers['Priority'] = config.priority
    if config.tags:
        if isinstance(config.tags, (list, tuple)):
            headers['Tags'] = ','.join(config.tags)
        else:
            headers['Tags'] = config.tags
    if config.title:
        headers['Title'] = config.title
    return headers


def _get_timestamp(ts_format):
    """Return the local time formatted with `ts_format`.

    See https://docs.python.org/3/library/time.html#time.strftime for string
    formatting options.
    """
    system_tz = tzlocal.get_localzone()
    now = dt.now(tz=system_tz)
    return now.strftime(ts_format)


def notify(config, message):
    """Send a notification.

    Arguments:
        config (dict): Parsed config from the config file.
        message (str): The body of the message to be sent.
    """
    server = config.server
    url = f'{server}/{config.topic}'
    headers = _get_headers(config)
    user = config.user
    password = config.password
    if config.user and config.password and config.token:
        raise NtfyrError(
            'Either user and password, or token can be specified, but not all '
            'of them.'  # nofmt
        )
    if (user and not password) or (not user and password):
        raise NtfyrError('Either user or password was specified but not both.')
    if user and password:
        credentials = (user, password)
    else:
        credentials = None
    if config.include_timestamp:
        timestamp = config.timestamp
        if '%message' in timestamp:
            # Replacing % notation with {} to avoid confusion with strftime
            message_format = timestamp.replace('%message', '{message}')
            message = _get_timestamp(message_format).format(message=message)
        else:
            message = f'{_get_timestamp(timestamp)} {message}'
    log.debug(
        'Sending request: method=POST, url=%s, headers=%s, auth.user=%s, '
        'data=%s',  # nofmt
        url,
        headers,
        user,
        message,
    )
    res = requests.post(
        url=url, headers=headers, data=message.encode('utf-8'), auth=credentials
    )
    try:
        log.debug('Got response: %s\n%s\n', res, res.json())
    except json.JSONDecodeError:
        log.error(
            'Failed to decode respones form ntfy. Got: %s',
            res.content.decode(),
        )
        raise NtfyrError(
            f'{res.status_code} {res.content.decode()}',
            server=server,
            topic=config.topic,
            message=message,
            headers=headers,
        )
    if not res.ok:
        if res.json():
            raise NtfyrError(
                '{error} {link}'.format(
                    error=res.json().get('error'),
                    link=res.json().get('link', ''),
                ),
                server=server,
                topic=config.topic,
                message=message,
                headers=headers,
            )
        raise NtfyrError(
            f'{res.status_code} {res.content.decode()}',
            server=server,
            topic=config.topic,
            message=message,
            headers=headers,
        )
