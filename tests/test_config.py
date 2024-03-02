import argparse
import os
import pathlib

import pytest

from ntfyr.__main__ import _parse_args
from ntfyr.config import (
    Config,
    NamespaceAdapter,
    _config_paths,
    _convert_source,
)
from ntfyr.errors import NtfyrConfigException


def test_config_paths_env_list(mocker):
    expected_paths = [
        pathlib.Path('path0'),
        pathlib.Path('path1'),
        pathlib.Path('path2'),
    ]
    mocker.patch.dict(
        os.environ,
        {'NTFYR_CONFIGS': 'path0:path1:path2'},
        clear=True,
    )
    actual_paths = _config_paths()
    assert actual_paths == expected_paths


def test_config_paths_env_xdg_home_config(mocker):
    home_dir = 'test value'
    expected_paths = [
        pathlib.Path('/etc/ntfyr/config.ini'),
        pathlib.Path('/usr/local/etc/ntfyr/config.ini'),
        pathlib.Path(home_dir).joinpath('ntfyr/config.ini'),
    ]
    mocker.patch.dict(
        os.environ,
        {'XDG_CONFIG_HOME': home_dir},
        clear=True,
    )
    actual_paths = _config_paths()
    assert actual_paths == expected_paths


def test_config_paths_fallback(mocker):
    home_dir = 'fake home'
    expected_paths = [
        pathlib.Path('/etc/ntfyr/config.ini'),
        pathlib.Path('/usr/local/etc/ntfyr/config.ini'),
        pathlib.Path(
            os.path.join(
                home_dir,
                '.config/ntfyr/config.ini',
            )
        ),
    ]
    mocker.patch.dict(os.environ, {'HOME': home_dir}, clear=True)
    actual_paths = _config_paths()
    assert actual_paths == expected_paths


def test_convert_source_dict_interface():
    class DictLike:
        get = None
        __contains__ = None

    expected_output = DictLike()
    actual_output = _convert_source(expected_output)
    assert actual_output is expected_output


def test_convert_source_args():
    actual_output = _convert_source(argparse.Namespace())
    assert isinstance(actual_output, NamespaceAdapter)


def test_convert_source_str(tmp_path):
    config_ini = tmp_path.joinpath('config.ini')
    config_ini.write_text('[ntfyr]\ntitle = test')
    expected_output = {'title': 'test'}
    actual_output = _convert_source(str(config_ini))
    assert actual_output == expected_output


def test_convert_source_path(tmp_path):
    config_ini = tmp_path.joinpath('config.ini')
    config_ini.write_text('[ntfyr]\ntitle = test')
    expected_output = {'title': 'test'}
    actual_output = _convert_source(config_ini)
    assert actual_output == expected_output


def test_convert_source_path_invalid_config(tmp_path):
    config_ini = tmp_path.joinpath('config.ini')
    config_ini.write_text('[bad_section]\ntitle = test')
    with pytest.raises(NtfyrConfigException):
        _convert_source(config_ini)


def test_convert_source_path_nonexistant(tmp_path):
    config_ini = tmp_path.joinpath('config.ini')
    assert not config_ini.exists()
    expected_output = {}
    actual_output = _convert_source(config_ini)
    assert actual_output == expected_output


def test_convert_source_path_bad_permissions(tmp_path):
    config_ini = tmp_path.joinpath('config.ini')
    config_ini.write_text('[ntfyr]\ntitle = test')
    config_ini.chmod(0o300)
    expected_output = {}
    actual_output = _convert_source(config_ini)
    try:
        assert actual_output == expected_output
    finally:
        config_ini.chmod(0o600)


def test_convert_source_invalid_type():
    with pytest.raises(NtfyrConfigException):
        _convert_source(None)


def test_namespace_adapter():
    namespace = argparse.Namespace(foo='foo', bar=None)
    adapter = NamespaceAdapter(namespace)
    assert 'foo' in adapter
    assert 'bar' not in adapter
    assert adapter.get('foo') == 'foo'
    assert adapter.get('bar', 1) == 1
    assert adapter['foo'] == 'foo'
    with pytest.raises(KeyError):
        adapter['bar']


def test_config_update_all():
    config = Config()
    config.update(
        {
            'topic': '1',
            'actions': '2',
            'attach': '3',
            'click': '4',
            'delay': '5',
            'email': '6',
            'priority': 'low',
            'tags': ['7'],
            'title': '8',
            'timestamp': '9',
            'server': '10',
            'user': '11',
            'password': '12',
        }
    )

    assert config.topic == '1'
    assert config.actions == '2'
    assert config.attach == '3'
    assert config.click == '4'
    assert config.delay == '5'
    assert config.email == '6'
    assert config.priority == 'low'
    assert config.tags == ['7']
    assert config.title == '8'
    assert config.include_timestamp is True
    assert config.timestamp == '9'
    assert config.server == '10'
    assert config.user == '11'
    assert config.password == '12'


def test_config_from_args(mocker, tmp_path):
    config_ini = tmp_path.joinpath('config.ini')
    config_ini.write_text('[ntfyr]\ntitle = test')
    args = [
        # fmt: off
        '--actions', 'actions value',
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
        # fmt: on
    ]
    namespace = _parse_args(args)
    assert isinstance(namespace, argparse.Namespace), (
        'The output from _parse args was not a `argparse.Namespace`. This '
        'invalidates this test'
    )
    mocker.patch.dict(os.environ, {}, clear=True)
    config = Config.from_args(namespace)
    assert config.topic == 'topic value'
    assert config.actions == 'actions value'
    assert config.attach == 'attach value'
    assert config.click == 'click value'
    assert config.delay == 'delay value'
    assert config.email == 'email value'
    assert config.priority == 'high'
    assert config.tags == ['tag0', 'tag1', 'tag2', 'tag3']
    assert config.title == 'title value'
    assert config.include_timestamp is True
    assert config.timestamp == 'timestamp'
    assert config.server == 'server value'
    assert config.user == 'user value'
    assert config.password == 'password value'


def test_config_update_int_tag():
    config = Config()
    config.update({'tags': 7})
    assert config.tags == ['7']


def test_config_update_invalid_str():
    config = Config()
    with pytest.raises(NtfyrConfigException):
        config.update({'topic': 1})


def test_config_update_invalid_choice():
    config = Config()
    with pytest.raises(NtfyrConfigException):
        # Pass type test to get to choice test
        config.update({'priority': 'banana'})
