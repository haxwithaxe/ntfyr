"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""

from .errors import (  # noqa: F401
    NtfyrConfigException,
    NtfyrError,
    NtfyrException,
)
from .ntfyr import notify  # noqa: F401
