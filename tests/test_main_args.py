
import pytest

from ntfyr.__main__ import _parse_args
from ntfyr.config import DEFAULT_TIMESTAMP


def test_parse_args_all():
    args = [
        '--actions', 'action value',
        '--attach', 'attach value',
        '--click', 'click value',
        '--delay', 'delay value',
        '--email', 'email value',
        '--priority', 'high',
        '--tags', 'tag0', 'tag1', 'tag2', 'tag3',
        '--title', 'title value',
        '--message', 'message value',
        '--timestamp', 'timestamp',
        '--topic', 'topic value',
        '--server', 'server value',
        '--user', 'user value',
        '--password', 'password value',
        '--config', 'config value',
        '--log-level', 'DEBUG'
    ]
    parsed = _parse_args(args)
    assert parsed.actions == 'action value'
    assert parsed.attach == 'attach value'
    assert parsed.click == 'click value'
    assert parsed.delay == 'delay value'
    assert parsed.email == 'email value'
    assert parsed.priority == 'high'
    assert parsed.tags == ['tag0', 'tag1', 'tag2', 'tag3']
    assert parsed.title == 'title value'
    assert parsed.message == 'message value'
    assert parsed.timestamp == 'timestamp'
    assert parsed.topic == 'topic value'
    assert parsed.server == 'server value'
    assert parsed.user == 'user value'
    assert parsed.password == 'password value'
    assert parsed.config == 'config value'
    assert parsed.log_level == 'DEBUG'


def test_parse_args_all_short():
    args = [
        '-A', 'action value',
        '-X', 'attach value',
        '-C', 'click value',
        '-D', 'delay value',
        '-E', 'email value',
        '-P', 'low',
        '-G', 'tag0', 'tag1', 'tag2', 'tag3',
        '-T', 'title value',
        '-m', 'message value',
        '-t', 'topic value',
        '-s', 'server value',
        '-u', 'user value',
        '-p', 'password value',
        '-c', 'config value'
    ]
    parsed = _parse_args(args)
    assert parsed.actions == 'action value'
    assert parsed.attach == 'attach value'
    assert parsed.click == 'click value'
    assert parsed.delay == 'delay value'
    assert parsed.email == 'email value'
    assert parsed.priority == 'low'
    assert parsed.tags == ['tag0', 'tag1', 'tag2', 'tag3']
    assert parsed.title == 'title value'
    assert parsed.message == 'message value'
    assert parsed.timestamp is None
    assert parsed.topic == 'topic value'
    assert parsed.server == 'server value'
    assert parsed.user == 'user value'
    assert parsed.password == 'password value'
    assert parsed.config == 'config value'
    assert parsed.log_level == 'ERROR'  # Default value


def test_parse_args_default_timestamp():
    args = ['--timestamp', '--topic', 'topic value']
    parsed = _parse_args(args)
    assert parsed.timestamp == DEFAULT_TIMESTAMP


def test_parse_args_invalid_topic():
    with pytest.raises(SystemExit):
        _parse_args([])


def test_parse_args_invalid_priority():
    with pytest.raises(SystemExit):
        _parse_args(['--priority', 'invalid priority'])


def test_parse_args_invalid_log_level():
    with pytest.raises(SystemExit):
        _parse_args(['--topic', 'good topic', '--log-level',
                     'invalid log level'])
