import pytest

from requisitor.session import Session


def test_UnitHTTPHandler(mocker):
    mocker.patch('urllib.request.HTTPHandler.do_open',
                 side_effect=RuntimeError)
    conn = mocker.patch('requisitor.handlers.UnixHTTPConnection')

    s = Session()
    with pytest.raises(RuntimeError):
        s.request('GET', 'http://foo/bar', unix_socket='foo')
    conn.assert_called_once_with('foo')
