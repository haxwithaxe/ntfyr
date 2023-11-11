"""End-to-end tests of ntfyr."""

import base64
import pathlib
from datetime import datetime

import pytest

from ntfyr.__main__ import main

from .fixtures.ntfy_server import MockNtfyServer


@pytest.mark.system
def test_parse_args_all(tmp_path: pathlib.Path, ntfy_server: MockNtfyServer):
    """An end-to-end test of ntfyr with all options set."""
    config_path = tmp_path.joinpath('ntfyr.ini')
    config_path.write_text('[ntfyr]\nlog_level = ERROR')
    username = 'username'
    password = 'password'
    date_format = '%Y-%m'
    message_value = 'message value'
    formatted_message = (
        f'{datetime.now().strftime(date_format)} {message_value}'  # nofmt
    )
    topic_value = 'test-topic'
    args = [
        '--actions',
        'action value',
        '--attach',
        'attach value',
        '--click',
        'click value',
        '--delay',
        '0',
        '--email',
        'test@example.com',
        '--priority',
        'low',
        '--tags',
        'tag0',
        'tag1',
        'tag2',
        'tag3',
        '--title',
        'title value',
        '--message',
        message_value,
        '--timestamp',
        date_format,
        '--topic',
        topic_value,
        '--server',
        ntfy_server.url,
        '--user',
        username,
        '--password',
        password,
        '--config',
        str(config_path),
        '--log-level',
        'DEBUG',
    ]
    main(args)
    request = ntfy_server.get_request()
    basic_credentials = (
        base64.encodebytes(f'{username}:{password}'.encode()).decode().strip()
    )
    assert request.path == f'/{topic_value}'
    assert request.content == formatted_message
    assert request.headers['Actions'] == 'action value'
    assert request.headers['Attach'] == 'attach value'
    assert request.headers['Click'] == 'click value'
    assert request.headers['Delay'] == '0'
    assert request.headers['Email'] == 'test@example.com'
    assert request.headers['Priority'] == 'low'
    assert request.headers['Tags'] == 'tag0,tag1,tag2,tag3'
    assert request.headers['Title'] == 'title value'
    assert request.headers['Authorization'] == f'Basic {basic_credentials}'
