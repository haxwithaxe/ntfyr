"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""

from .ntfyr import notify
from .errors import NtfyrConfigException, NtfyrError, NtfyrException
