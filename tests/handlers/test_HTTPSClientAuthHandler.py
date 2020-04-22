import pytest

from requisitor.session import Session


def test_client_cert_auth(mocker):
    conn = mocker.patch('http.client.HTTPSConnection',
                        side_effect=RuntimeError)

    s = Session()
    with pytest.raises(RuntimeError):
        s.request('GET', 'https://foo.bar', cert=('cert', 'key'))

    args, kwargs = conn.call_args
    assert kwargs['cert_file'] == 'cert'
    assert kwargs['key_file'] == 'key'


def test_unix_socket(mocker):
    conn = mocker.patch('requisitor.handlers.UnixHTTPSConnection',
                        side_effect=RuntimeError)

    s = Session()
    with pytest.raises(RuntimeError):
        s.request('GET', 'https://foo.bar', unix_socket='/foo/bar')

    conn.assert_called_once()
