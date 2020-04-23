from unittest.mock import MagicMock

import pytest

from requisitor.handlers import UnixHTTPConnection


def test_connect(mocker):
    mocker.patch('socket.socket')

    conn = UnixHTTPConnection('foo')
    conn('host').connect()


def test_connect_OSError(mocker):
    socket = MagicMock()
    socket.connect = MagicMock(side_effect=OSError)
    mocker.patch('socket.socket', return_value=socket)

    conn = UnixHTTPConnection('foo')
    with pytest.raises(OSError, match=r'Invalid Socket File \(foo\)'):
        conn('host').connect()


def test_connect_timeout(mocker):
    socket = MagicMock()
    mocker.patch('socket.socket', return_value=socket)
    conn = UnixHTTPConnection('foo')
    conn('host', timeout=1).connect()
    socket.settimeout.assert_called_once_with(1)


def test_call(mocker):
    init = mocker.patch('http.client.HTTPConnection.__init__')
    conn = UnixHTTPConnection('foo')
    assert conn('host') is conn
    init.assert_called_once()
