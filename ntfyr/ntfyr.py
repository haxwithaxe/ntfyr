"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""


from datetime import datetime as dt
import requests
import tzlocal

from .errors import NtfyrMissingValueError, NtfyrError


DEFAULT_PRIORITY = 'default'
DEFAULT_SERVER = 'https://ntfy.sh'
DEFAULT_TIMESTAMP = '%Y-%m-%d %H:%M:%S %Z'


def _get_timestamp(timestamp_format):
    """Returns the local time formatted with `timestamp_format`.

    See https://docs.python.org/3/library/time.html#time.strftime for string
    formatting options.
    """
    system_tz = tzlocal.get_localzone()
    now = dt.now(tz=system_tz)
    return now.strftime(timestamp_format)


class Ntfyr:
    """Reusable notification.

    Most of the arguments and attributes map directly to parts of the ntfy.sh message publication API (https://ntfy.sh/docs/publish/). This class uses the HTTP POST API and more details about the format and content of the arguments can be found in the documentation for that API.

    Arguments:
        message (str, optional): The message to publish to `topic` on `server`.
        topic (str, optional): The topic on `server` to publish the message to.
        server (str, optional): The server to publish `message` to. Defaults to `DEFAULT_SERVER`. This can contain a port and/or additional path. For example `https://example.com:4443/ntfy`.
        timestamp (str, optional): The timestamp format (see https://docs.python.org/3/library/time.html#time.strftime) or `True` for the default timestamp format. Defaults to no timestamp. If the string `%message` is present in `timestamp` it will be replaced with the message and the timestamp with the embedded message used in place of the original message. For example `%Y/%m/%d %message %Z` would become `2022/07/18 Hello, World! UTC`.
        user (str, optional): The username to authenticate to `server`.
        password (str, optional): The password to authenticate to `server`.
        actions (str, optional): See the HTTP header format in https://ntfy.sh/docs/publish/#action-buttons for details.
        attach (str, optional): See the HTTP header format in https://ntfy.sh/docs/publish/#attachments for details.
        click (str, optional): See the HTTP header format in https://ntfy.sh/docs/publish/#click-action for details.
        delay (str, optional): See the HTTP header format in https://ntfy.sh/docs/publish/#scheduled-delivery for details.
        email (str, optional): See the HTTP header format in https://ntfy.sh/docs/publish/#e-mail-notifications for details.
        priority (Priority, optional): The priority to publish the notification under. Defaults to `DEFAULT_PRIORITY`.
        tags (list[str], optional): A list of tags. See the HTTP header format in https://ntfy.sh/docs/publish/#tags-emojis for details. This can also be a comma separated list of tags which will be converted to a list.
        title (str, optional): The title to give the notification.

    Attributes:
        message (str): The formatted message.
        timestamp (str): The timestamp format to prepend to the message.
        topic (str): The topic to publish the message to.
        server (str): The server to publish the message to.
        user (str): The user to authenticate to the server with.
        password (str): The password to authenticate to the server with.
        actions (str): The actions to publish with the message.
        attach (str): The attachments to publish with the message.
        click (str): The "click" action value.
        delay (str): The delay interval to pass to the server.
        email (str): The email address to pass to the server.
        priority (str or int): The priority to publish the message under.
        tags (list): A list of tags to tags to attach to the message.
        title (str): The title of the message.

    """

    def __init__(
        self,
        message=None,
        topic=None,
        server=DEFAULT_SERVER,
        timestamp=None,
        user=None,
        password=None,
        actions=None,
        attach=None,
        click=None,
        delay=None,
        email=None,
        priority=DEFAULT_PRIORITY,
        tags=None,
        title=None,
        **_
    ):
        self._message = message
        self.topic = topic
        self.server = server or DEFAULT_SERVER
        self.timestamp = DEFAULT_TIMESTAMP if timestamp is True else timestamp
        self.user = user
        self.password = password
        self.actions = actions
        self.attach = attach
        self.click = click
        self.delay = delay
        self.email = email
        self.priority = priority
        self.tags = tags
        if tags and not isinstance(tags, (list, tuple)):
            self.tags = tags.split(',')
        self.title = title

    @property
    def _credentials(self):
        if self.user and self.password:
            return (self.user, self.password)
        if (self.user and not self.password) or (not self.user and self.password):
            raise NtfyrError('Either user or password was specified but not both.')
        return None

    @property
    def message(self):
        if self.timestamp:
            if '%message' in self.timestamp:
                # Replacing % notation with {} to avoid confusion with strftime
                message_format = self.timestamp.replace(
                    '%message',
                    '{message}'
                )
                return _get_timestamp(message_format).format(self._message)
            else:
                return f'{_get_timestamp(self.timestamp)} {self._message}'
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    @property
    def _headers(self):
        """Get headers from arguments and configs."""
        headers = {}
        if self.actions:
            headers['Actions'] = self.actions
        if self.attach:
            headers['Attach'] = self.attach
        if self.click:
            headers['Click'] = self.click
        if self.delay:
            headers['Delay'] = self.delay
        if self.email:
            headers['Email'] = self.email
        if self.priority:
            headers['Priority'] = self.priority
        if self.tags:
            headers['Tags'] = ','.join(self.tags)
        if self.title:
            headers['Title'] = self.title
        return headers

    def notify(self, message=None, topic=None, **config):
        """Send a notification.

        Arguments given here override but do not overwrite the values set in
        the `Ntfyr` instance.

        Note:
            See the `ntfyr.Ntfyr` constructor for full list of arguments. The
            following are optional positional arguments.

        Arguments:
            message (str, optional): The body of the message to be sent.
            topic (str, optional): The topic to publish the notification to.

        Keyword Arguments:
            config: See `ntfyr.Ntfyr` constructor for a full list of arguments.

        """
        # Calling out message and topic to allow users to use them positionally
        #   under the assumption that they are likely to be used frequently.
        # If any overrides are given use a temporary copy of the Ntfyr instance
        #   to avoid duplicating code.
        if message or topic or config:
            kwargs = self.__dict__.copy()
            kwargs.update(config)
            if message:
                kwargs['message'] = message
            if topic:
                kwargs['topic'] = topic
            Ntfyr(**kwargs).notify()
            return
        # Otherwise send the notification.
        if not self._message:
            raise NtfyrMissingValueError('message')
        if not self.topic:
            raise NtfyrMissingValueError('topic')
        if not self.server:
            raise NtfyrMissingValueError('server')
        url = f'{self.server}/{self.topic}'
        res = requests.post(url=url, headers=self._headers, data=self.message.encode('utf-8'),
                            auth=self._credentials)
        if not res.ok:
            if res.json():
                raise NtfyrError('{error} {link}'.format(**res.json()),
                                 self.server, self.topic, self._headers,
                                 self.message)
            raise NtfyrError(f'{res.status_code} {res.content.decode()}',
                             self.server, self.topic, self._headers,
                             self.message)
