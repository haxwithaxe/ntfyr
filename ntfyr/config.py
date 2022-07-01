"""A tool to send notifications to https://ntfy.sh

This is just the backend of the ntfyr script.
"""


import argparse
import configparser
import os

from ._common import log
from .errors import NtfyrConfigException


class NamespaceAdapter:

    def __init__(self, namespace):
        self._namespace = namespace

    def get(self, key, default=None):
        if hasattr(self._namespace, key):
            return getattr(self._namespace, key)
        return default

    def __getitem__(self, key):
        if hasattr(self._namespace, key):
            return getattr(self._namespace, key)
        raise KeyError(key)


class Config:

    def __init__(self, *sources):
        self._souces = []
        for source in sources:
            self.add_source(source)

    def add_source(self, source):
        if hasattr(source, 'get'):
            self._souces.append(source)
        elif isinstance(source, argparse.Namespace):
            self._souces.append(NamespaceAdapter(source))
        elif isinstance(source, str):
            if not os.path.exists(source):
                log.warn('The config source "%s" does not exist.', source)
                return
            confparser = configparser.ConfigParser(defaults={})
            confparser.read(source)
            try:
                self._souces.append(confparser['ntfyr'])
            except KeyError:
                raise NtfyrConfigException(f'Invalid config source: {source}')
        else:
            raise NtfyrConfigException(f'Unknown source type {source}')

    def get(self, key, default=None):
        for source in self._souces:
            if source.get(key) is not None:
                return source.get(key)
        return default
