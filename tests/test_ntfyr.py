"""The main `ntfyr` functionality."""

from collections import namedtuple
from datetime import datetime as dt

import pytest

from ntfyr.config import Config
from ntfyr.errors import NtfyrError
from ntfyr.ntfyr import _get_headers, _get_timestamp, notify


def _too_close_to_midnight(seconds_till=2):
    now = dt.now()
    if now.hour == 23 and now.minute == 59 and now.second < (59 - seconds_till):
        return True
    return False


def _mock_post_factory():
    context = {}

    def _mock_post(url, headers, data, auth):
        context.update(dict(url=url, headers=headers, data=data, auth=auth))
        return namedtuple(
            'mock_response',
            ['ok', 'json'],
            defaults=[True, lambda: {}],
        )()

    return context, _mock_post


def _mock_post_error_factory(with_json=True):
    context = {}
    status_code = 500
    content = b'content value'
    context['output_values'] = {'status_code': status_code, 'content': content}

    def _mock_post(url, headers, data, auth):
        context.update(dict(url=url, headers=headers, data=data, auth=auth))
        json = {'error': 'error text', 'link': 'error link'}
        return namedtuple(
            'mock_response',
            ['ok', 'json', 'status_code', 'content'],
            defaults=[
                False,
                lambda: json if with_json else None,
                status_code,
                content,
            ],
        )()

    return context, _mock_post


def test_get_headers_all():
    config = Config(
        actions='actions value',
        attach='attach value',
        click='click value',
        delay='delay value',
        email='email value',
        priority='default',
        tags=['tag0', 'tag1', 'tag2'],
        title='title value',
    )
    headers = _get_headers(config)
    assert headers['Actions'] == config.actions
    assert headers['Attach'] == config.attach
    assert headers['Click'] == config.click
    assert headers['Delay'] == config.delay
    assert headers['Email'] == config.email
    assert headers['Priority'] == config.priority
    assert headers['Tags'] == ','.join(config.tags)
    assert headers['Title'] == config.title


def test_get_headers_none():
    config = Config()
    headers = _get_headers(config)
    assert headers == {}


def test_get_timestamp(mocker):
    # Chose a day rather than a time so that the likelyhood of a race condition
    #   between the two formatting operations is low.
    date_format = '%Y-%m-%d'
    timestamp = _get_timestamp(date_format)
    expected_timestamp = dt.now().strftime(date_format)
    assert timestamp == expected_timestamp


@pytest.mark.skipif(
    _too_close_to_midnight(),
    reason='Too close to midnight. Timestamp might be wrong erroneously.',
)
def test_notify_kitchen_sink(mocker):
    message = 'test message'  # Must not contain time format variables
    context, mock_post = _mock_post_factory()
    mocker.patch('ntfyr.ntfyr.requests.post', mock_post)
    config = Config(
        topic='topic value',
        # Headers
        actions='actions value',
        attach='attach value',
        click='click value',
        delay='delay value',
        email='email value',
        priority='priority value',
        tags=['tag0', 'tag1', 'tag2'],
        title='title value',
        # Config
        include_timestamp=True,
        timestamp='timestamp value: %Y-%m',
        server='server value',
        user='user value',
        password='password value',
    )
    notify(config, message)
    # Headers
    assert context['headers']['Actions'] == config.actions
    assert context['headers']['Attach'] == config.attach
    assert context['headers']['Click'] == config.click
    assert context['headers']['Delay'] == config.delay
    assert context['headers']['Email'] == config.email
    assert context['headers']['Priority'] == config.priority
    assert context['headers']['Tags'] == ','.join(config.tags)
    assert context['headers']['Title'] == config.title
    # Config
    assert context['auth'] == (config.user, config.password)
    assert context['url'] == f'{config.server}/{config.topic}'
    # Message/timestamp
    assert (
        context['data']
        == dt.now().strftime(f'timestamp value: %Y-%m {message}').encode()
    )


def test_notify_error_with_json(mocker):
    message = 'test message'  # Must not contain time format variables
    context, mock_post = _mock_post_error_factory()
    mocker.patch('requests.post', mock_post)
    config = Config(
        topic='topic value',
        # Headers
        priority='priority value',
        # Config
        include_timestamp=False,
        timestamp=None,
        server='server value',
    )
    with pytest.raises(NtfyrError) as err:
        notify(config, message)
    assert err.value.message == '{error} {link}'.format(
        error='error text', link='error link'
    )
    assert err.value.headers == {'Priority': config.priority}
    assert err.value.topic == config.topic
    assert err.value.server == config.server
    # Config
    assert context['url'] == f'{config.server}/{config.topic}'
    # Message/timestamp
    assert context['data'] == message.encode()


def test_notify_error_without_json(mocker):
    message = 'test message'  # Must not contain time format variables
    context, mock_post = _mock_post_error_factory(with_json=False)
    expected_error_message = (
        f'{context["output_values"]["status_code"]} '
        f'{context["output_values"]["content"].decode()}'
    )
    mocker.patch('ntfyr.ntfyr.requests.post', mock_post)
    config = Config(
        topic='topic value',
        # Headers
        priority='priority value',
        # Config
        include_timestamp=False,
        timestamp=None,
        server='server value',
    )
    with pytest.raises(NtfyrError) as err:
        notify(config, message)
    assert err.value.message == expected_error_message
    assert err.value.headers == {'Priority': config.priority}
    assert err.value.topic == config.topic
    assert err.value.server == config.server
    # Config
    assert context['url'] == f'{config.server}/{config.topic}'
    # Message/timestamp
    assert context['data'] == message.encode()
