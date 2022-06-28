
import requests


DEFAULT_SERVER = 'https://ntfy.sh'


class NtfyrError(Exception):
    """ntfyr flow control error

    Arguments:
        error (str): Message for the user.
        server (str, optional): The server name specified as an argument or in the config.
        topic (str, optional): The topic name specified as an argument or in the config.
        headers (dict, optional): The headers specified as an argument or in the config.
        message (str, optional): The message body specified as an argument or in the config.
    """

    def __init__(self, error, server=None, topic=None, message=None, headers=None):
        super().__init__(error)
        self.message = error
        self.server = server
        self.topic = topic
        self._message = message
        self.headers = headers


def _get_headers(args, config):
    """Get headers from arguments and configs."""
    headers = {}
    if args.actions or config.get('actions'):
        headers['Actions'] = args.actions or config.get('actions')
    if args.attach or config.get('attach'):
        headers['Attach'] = args.attach or config.get('attach')
    if args.click or config.get('click'):
        headers['Click'] = args.click or config.get('click')
    if args.delay or config.get('delay'):
        headers['Delay'] = args.delay or config.get('delay')
    if args.email or config.get('email'):
        headers['Email'] = args.email or config.get('email')
    if args.priority or config.get('priority'):
        headers['Priority'] = args.priority or config.get('priority')
    if config.get('tags'):
        headers['Tags'] = config.get('tags')
    if args.tags:  # Override default tags
        headers['Tags'] = ','.join(args.tags)
    if args.title or config.get('title'):
        headers['Title'] = args.title or config.get('title')
    return headers


def notify(args, config, message):
    """Send a notification.

    Arguments:
        args (argparse.Namespace): The arguments passed to the script.
        config (dict): Parsed config from the config file.
        message (str): The body of the message to be sent.
    """
    server = args.server or config.get('server', DEFAULT_SERVER)
    url = f'{server}/{args.topic}'
    headers = _get_headers(args, config)
    user = args.user or config.get('user', '')
    password = args.password or config.get('password', '')
    if user and password:
        credentials = (user, password)
    elif (user and not password) or (not user and password):
        raise NtfyrError('Either user or password was specified but not both.')
    else:
        credentials = None
    res = requests.post(url=url, headers=headers, data=message, auth=credentials)
    if not res.ok:
        if res.json():
            raise NtfyrError('{error} {link}'.format(**res.json()), server,
                             args.topic, headers, message)
        raise NtfyrError(f'{res.status_code} {res.content.decode()}', server,
                         args.topic, headers, message)
