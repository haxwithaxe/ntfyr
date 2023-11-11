"""A super simple mock ntfy server."""

import http.server
import io
import socket
import socketserver
import threading
import time
from dataclasses import dataclass
from typing import Callable

import pytest


class NoFeePort(Exception):
    """A descriptive exception for when no free port is found."""


class _Ports:
    """A registry of ports use in testing."""

    _claimed: list[int] = []
    """A list of claimed ports."""

    @classmethod
    def claim(cls, port: int) -> bool:
        """Attempt to claim a port.

        Arguments:
            port: The port number to be claimed.

        Returns:
            `True` if the port is not claimed already. `False` if it is
            claimed.
        """
        if port in cls._claimed:
            return False
        cls._claimed.append(port)
        return True

    @classmethod
    def free_port(
        cls,
        min_port: int = 1025,
        max_port: int = 65535,
        address: str = '127.0.0.1',
    ) -> int:
        """Return the first free port between `min_port` and `max_port`.

        The range between `min_port` and `max_port` is inclusive.

        Note:
            This uses a global registry of selected ports so the previously
            discovered free ports don't have to be in use when selecting
            another free port.

        Arguments:
            min_port: The lowest acceptable port. Defaults to 1025.
            max_port: The highest acceptable port. Defaults to 65535.
            address: The address to bind to. Defaults to `'127.0.0.1'`.

        Returns:
            A free port between `min_port` and `max_port` (inclusive).

        Raises:
           NoFreePort: When there are no unused ports in the given range.
        """
        for port in range(min_port, max_port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind((address, port))
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if cls.claim(port):
                    # Only close the socket on a successful connection or at
                    #   the
                    #   end of the process.
                    sock.close()
                    return port
            except OSError:
                pass
            finally:
                sock.close()
        raise NoFeePort()


class _RequestHandler(http.server.BaseHTTPRequestHandler):
    _consume_request: Callable[[str, dict, io.BufferedIOBase], None] = None

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        message = self.rfile.read(content_length)
        self._consume_request(self.path, self.headers, message.decode())
        echo = f'{{"message": "{message.decode()}"}}'.encode("utf-8")
        self.send_response(http.server.HTTPStatus.ACCEPTED)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', str(len(echo)))
        self.end_headers()
        self.wfile.write(echo)
        self.wfile.flush()


@dataclass
class _Request:
    path: str = None
    headers: dict = None
    content: str = None


class MockNtfyServer(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, daemon=True, **kwargs)
        self.port: int = _Ports.free_port()
        self._request: _Request = None

    @property
    def url(self) -> str:
        return f'http://localhost:{self.port}'

    def _consume_request(self, path: str, headers: dict, content: str):
        self._request = _Request(path, headers, content)

    def run(self):
        _RequestHandler._consume_request = self._consume_request
        address = ('localhost', self.port)
        with socketserver.TCPServer(address, _RequestHandler) as sock:
            sock.handle_request()

    def get_request(self) -> _Request:
        while self.is_alive():
            time.sleep(0.01)
        self.join()
        return self._request


@pytest.fixture()
def ntfy_server():
    server = MockNtfyServer()
    server.start()
    yield server
    server.join()
