"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""


class NtfyrException(Exception):
    pass


class NtfyrConfigException(NtfyrException):
    pass


class NtfyrMissingValueError(NtfyrException):

    def __init__(self, value):
        super().__init__('Missing `{value}` value.')
        self.value = value


class NtfyrInvalidValueError(NtfyrException):

    def __init__(self, key, value):
        super().__init__('Invalid value "{value}" for `{key}`.')
        self.key = key
        self.value = value


class NtfyrError(NtfyrException):
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
