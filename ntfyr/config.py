"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""


import argparse
import configparser
from dataclasses import dataclass, field
import os
import pathlib

from ._common import log
from .errors import NtfyrConfigException

DEFAULT_SERVER = 'https://ntfy.sh'
DEFAULT_TIMESTAMP = '%Y-%m-%d %H:%M:%S %Z'
PRIORITIES = ['max', 'urgent', 'high', 'default', 'low', 'min', '1', '2', '3',
              '4', '5']


def _config_paths():
    paths = []
    if os.environ.get('NTFYR_CONFIGS'):
        paths.extend(os.environ['NTFYR_CONFIGS'].split(':'))
    else:
        paths.extend(['/etc/ntfyr/config.ini',
                      '/usr/local/etc/ntfyr/config.ini'])
        if os.environ.get('XDG_CONFIG_HOME'):
            paths.append(os.environ['XDG_CONFIG_HOME'])
        elif os.environ.get('HOME'):
            paths.append(os.path.join(os.environ['HOME'],
                                      '.config/ntfyr/config.ini'))
    return [pathlib.Path(p) for p in paths]


def _convert_source(source):
    if hasattr(source, 'get') and hasattr(source, '__contains__'):
        return source
    elif isinstance(source, argparse.Namespace):
        return NamespaceAdapter(source)
    elif isinstance(source, (str, pathlib.Path)):
        source = pathlib.Path(source)
        if not source.exists():
            log.warning('The config source "%s" does not exist.', source)
            return
        try:
            config_text = source.read_text()
        except OSError as err:
            log.warning('Failed to read config source %s: %s: %s',
                        source.absolute(), err.__class__.__name__, err)
            return {}
        confparser = configparser.ConfigParser(defaults={})
        confparser.read_string(config_text)
        try:
            return dict(confparser['ntfyr'])
        except KeyError:
            raise NtfyrConfigException(f'Invalid config source: {source}')
    else:
        raise NtfyrConfigException(f'Unknown source type {source}')


class NamespaceAdapter:
    """An adapter for `argparse.Namespace` objects.

    This provides a `dict`-like interface.

    Arguments:
        namespace:
    """

    def __init__(self, namespace):
        self._namespace = namespace

    def get(self, key, default=None):
        if (hasattr(self._namespace, key) and
                getattr(self._namespace, key) is not None):
            return getattr(self._namespace, key)
        return default

    def __contains__(self, key):
        return (hasattr(self._namespace, key) and
                getattr(self._namespace, key) is not None)

    def __getitem__(self, key):
        if hasattr(self._namespace, key):
            return getattr(self._namespace, key)
        raise KeyError(key)


@dataclass
class Config:

    topic: str = None
    actions: str = None
    attach: str = None
    click: str = None
    delay: str = None
    email: str = None
    priority: str = None
    tags: list[str] = field(default_factory=list)
    title: str = None
    include_timestamp: bool = False
    timestamp: str = None
    server: str = DEFAULT_SERVER
    user: str = None
    password: str = None

    def _typed_set(self, attr, value, required_type, choices=None):
        if not isinstance(value, required_type):
            raise NtfyrConfigException(f'Invalid value for `{attr}`: {value}')
        if choices and value not in choices:
            raise NtfyrConfigException(f'Invalid value for `{attr}`: {value}')
        setattr(self, attr, value)

    def update(self, source):
        source = _convert_source(source)
        for key, required_type in self.__annotations__.items():
            if key not in source:
                continue
            value = source.get(key)
            if key == 'priority':
                self._typed_set(key, value, required_type, PRIORITIES)
                continue
            if key == 'tags':
                if value and isinstance(value, str):
                    value = [value]
                tags = []
                for tag in value:
                    if not tag and not isinstance(tag, int):
                        raise NtfyrConfigException(
                            f'Invalid value for `tags`: {value}'
                        )
                    tags.append(tag)
                self.tags = tags
                continue
            if key == 'timestamp' and source.get('timestamp'):
                self.include_timestamp = True
            self._typed_set(key, source.get(key), required_type)

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default

    def search(self):
        for source in _config_paths():
            self.update(source)
