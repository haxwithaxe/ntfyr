"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""


from datetime import datetime as dt
import requests
import tzlocal

from .errors import NtfyrError


DEFAULT_SERVER = 'https://ntfy.sh'


class Ntfyr:

    def __init__(self, config):
        self._config = config

    def update(self, **config):
        self._config.update(config)

    def _get_headers(self):
        """Get headers from arguments and configs."""
        headers = {}
        if self._config.get('actions'):
            headers['Actions'] = self._config.get('actions')
        if self._config.get('attach'):
            headers['Attach'] = self._config.get('attach')
        if self._config.get('click'):
            headers['Click'] = self._config.get('click')
        if self._config.get('delay'):
            headers['Delay'] = self._config.get('delay')
        if self._config.get('email'):
            headers['Email'] = self._config.get('email')
        if self._config.get('priority'):
            headers['Priority'] = self._config.get('priority')
        if self._config.get('tags'):
            tags = self._config.get('tags')
            if isinstance(tags, (list, tuple)):
                tags = ','.join(tags)
            headers['Tags'] = tags
        if self._config.get('title'):
            headers['Title'] = self._config.get('title')
        return headers


    def _get_timestamp(self, message_format=None):
        """Returns the local time formatted with `ts_format`.

        See https://docs.python.org/3/library/time.html#time.strftime for string
        formatting options.
        """
        system_tz = tzlocal.get_localzone()
        now = dt.now(tz=system_tz)
        return now.strftime(message_format or self._config.get('timestamp'))


    def _format_message(self, message):
        if self._config.get('timestamp'):
            if '%message' in self._config.get('timestamp'):
                # Replacing % notation with {} to avoid confusion with strftime
                message_format = self._config.get('timestamp').replace(
                    '%message',
                    '{message}'
                )
                return self._get_timestamp(message_format).format(
                    message=message
                )
            else:
                return f'{self._get_timestamp()} {message}'
        return message

    def notify(self, message, topic=None):
        """Send a notification.

        Arguments:
            message (str): The body of the message to be sent.
        """
        server = self._config.get('server', DEFAULT_SERVER)
        url = f'{server}/{self._config.get("topic")}'
        headers = self._get_headers()
        user = self._config.get('user', '')
        password = self._config.get('password', '')
        if user and password:
            credentials = (user, password)
        elif (user and not password) or (not user and password):
            raise NtfyrError('Either user or password was specified but not both.')
        else:
            credentials = None
        message = self._format_message(message)
        res = requests.post(url=url, headers=headers, data=message.encode('utf-8'),
                            auth=credentials)
        if not res.ok:
            if res.json():
                raise NtfyrError('{error} {link}'.format(**res.json()), server,
                                 self._config.get('topic'), headers, message)
            raise NtfyrError(f'{res.status_code} {res.content.decode()}', server,
                             self._config.get('topic'), headers, message)
