"""Errors raised by `ntfyr`."""


class NtfyrException(Exception):
    """Base class for exceptions raised by `ntfyr`."""


class NtfyrConfigException(NtfyrException):
    """Indicates an error in a `ntfyr` config file."""


class NtfyrError(NtfyrException):
    """An exception that indicates a fatal error.

    Arguments:
        error (str): Message for the user.
        server (str, optional): The server name specified as an argument or in
            the config.
        topic (str, optional): The topic name specified as an argument or in
            the config.
        headers (dict, optional): The headers specified as an argument or in
            the config.
        message (str, optional): The message body specified as an argument or
            in the config.
    """

    def __init__(
        self,
        error,
        server=None,
        topic=None,
        message=None,
        headers=None,
    ):  # noqa: D107
        super().__init__(error)
        self.message = error
        self.server = server
        self.topic = topic
        self._message = message
        self.headers = headers
