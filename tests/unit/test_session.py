import http.cookiejar
import pathlib
import ssl
from unittest.mock import MagicMock
from unittest.mock import call
from urllib.request import HTTPDigestAuthHandler

import pytest

import requisitor.session
from requisitor.auth import HTTPDigestAuth
from requisitor.handlers import UnixHTTPHandler
from requisitor.headers import Headers
from requisitor.sentinel import Sentinel


fixtures = pathlib.Path(__file__).parent / 'fixtures'


@pytest.fixture
def session(monkeypatch):
    s = requisitor.session.Session()
    monkeypatch.setattr(s, 'request', MagicMock())
    return s


@pytest.fixture
def full_session(monkeypatch, mocker):
    s = requisitor.session.Session()
    opener = MagicMock()
    build_opener = mocker.patch('urllib.request.build_opener',
                                return_value=opener)
    response = MagicMock()
    monkeypatch.setattr(requisitor.session, 'Response', response)
    return s, build_opener, opener, response


def test_get(session):
    session.get('http://foo.bar/', headers={})

    session.request.assert_called_once_with('GET', 'http://foo.bar/',
                                            headers={})


def test_options(session):
    session.options('http://foo.bar/', headers={})

    session.request.assert_called_once_with('OPTIONS', 'http://foo.bar/',
                                            headers={})


def test_head(session):
    session.head('http://foo.bar/', headers={})

    session.request.assert_called_once_with('HEAD', 'http://foo.bar/',
                                            headers={})


def test_post(session):
    session.post('http://foo.bar/', data='baz', headers={})

    session.request.assert_called_once_with('POST', 'http://foo.bar/',
                                            data='baz', headers={})


def test_put(session):
    session.put('http://foo.bar/', data='baz', headers={})

    session.request.assert_called_once_with('PUT', 'http://foo.bar/',
                                            data='baz', headers={})


def test_patch(session):
    session.patch('http://foo.bar/', data='baz', headers={})

    session.request.assert_called_once_with('PATCH', 'http://foo.bar/',
                                            data='baz', headers={})


def test_delete(session):
    session.delete('http://foo.bar/', headers={})

    session.request.assert_called_once_with('DELETE', 'http://foo.bar/',
                                            headers={})


def test_auth(session):
    assert session.auth is None
    session.auth = ('foo', 'bar')
    assert session.auth is not None


def test_validate_cert():
    vc = requisitor.session._validate_cert
    assert vc(None) is None
    pytest.raises(TypeError, vc, ())
    pytest.raises(TypeError, vc, ('foo',))
    pytest.raises(TypeError, vc, True)
    assert vc(('foo', 'bar')) == ('foo', 'bar')


def test_cert(session):
    assert session.cert is None
    session.cert = ('foo', 'bar')
    assert session.cert is not None


def test_headers(session):
    assert isinstance(session.headers, Headers)
    session.headers = {'foo': 'bar'}
    assert isinstance(session.headers, Headers)
    assert session.headers['foo'] == 'bar'


def test_fallback(session):
    assert session._fallback(True, None) is True
    assert session._fallback(True, 'foo') is True
    assert session._fallback(Sentinel, True) is True


def test_create_context(session):
    context = session._create_context(False)
    assert context.check_hostname is False
    assert context.verify_mode == ssl.CERT_NONE

    context = session._create_context(True)
    assert context.check_hostname is not False
    assert context.verify_mode != ssl.CERT_NONE

    count = len(context.get_ca_certs())
    context = session._create_context(
        fixtures / 'cacert.pem'
    )
    assert count + 1 == len(context.get_ca_certs())


def test_request_files(full_session):
    session, build_opener, opener, response = full_session

    with pytest.raises(NotImplementedError):
        session.request('GET', 'http://foo.bar', files='foo')


def test_request_data_json(full_session):
    session, build_opener, opener, response = full_session

    with pytest.raises(TypeError):
        session.request('GET', 'http://foo.bar', data='foo', json='bar')

    session.request('GET', 'http://foo.bar')


def test_request_fallbacks(full_session, monkeypatch):
    session, build_opener, opener, response = full_session
    session.params['foo'] = 'bar'
    session.headers['baz'] = 'qux'

    calls = [
        call(Sentinel, None),  # auth
        call(Sentinel, None),  # cert
        call(Sentinel, session.cookies),  # cookies
        call(Sentinel, None),  # unix_socket
        call(Sentinel, None),  # verify
    ]

    _fallback = MagicMock(return_value=None)
    monkeypatch.setattr(session, '_fallback', _fallback)

    session.request('GET', 'http://foo.bar')

    _fallback.assert_has_calls(calls)
    assert _fallback.call_count == 5

    args, kwargs = opener.open.call_args
    request = args[0]
    assert request.full_url == 'http://foo.bar?foo=bar'
    assert dict(request.headers) == {'Baz': 'qux'}


def test_request_overrides(full_session, monkeypatch):
    session, build_opener, opener, response = full_session
    session.params['foo'] = 'bar'
    session.headers['baz'] = 'qux'

    cookies = http.cookiejar.CookieJar()

    calls = [
        call(('foo', 'bar'), None),  # auth
        call(('cert', 'key'), None),  # cert
        call(cookies, session.cookies),  # cookies
        call(True, None),  # unix_socket
        call(False, None),  # verify
    ]

    _fallback = MagicMock(return_value=None)
    monkeypatch.setattr(session, '_fallback', _fallback)

    session.request('GET', 'http://foo.bar', auth=('foo', 'bar'),
                    cert=('cert', 'key'), cookies=cookies, unix_socket=True,
                    verify=False, headers={'baz': 'foo', 'here': 'i am'},
                    params={'foo': 'baz', 'another': 'one'})

    _fallback.assert_has_calls(calls)
    assert _fallback.call_count == 5

    args, kwargs = opener.open.call_args
    request = args[0]
    assert request.full_url == 'http://foo.bar?foo=baz&another=one'
    assert dict(request.headers) == {'Baz': 'foo', 'Here': 'i am'}


def test_request_auth(full_session):
    session, build_opener, opener, response = full_session

    session.request('GET', 'http://foo.bar', auth=('foo', 'bar'))

    args, kwargs = opener.open.call_args
    request = args[0]
    assert request.headers['Authorization'] == 'Basic Zm9vOmJhcg=='


def test_request_digest(full_session):
    session, build_opener, opener, response = full_session

    session.request('GET', 'http://foo.bar', auth=HTTPDigestAuth('foo', 'bar'))

    args, kwargs = build_opener.call_args
    h = [h for h in args if isinstance(h, HTTPDigestAuthHandler)]
    assert len(h) == 1


def test_request_json(full_session):
    session, build_opener, opener, response = full_session

    session.request('POST', 'http://foo.bar', json={'foo': 'bar'})

    args, kwargs = opener.open.call_args
    request = args[0]

    assert request.method == 'POST'
    assert request.data == b'{"foo": "bar"}'
    assert request.headers['Content-type'] == 'application/json'


def test_request_json_headers_encode(full_session, mocker):
    session, build_opener, opener, response = full_session

    dumps = mocker.patch('json.dumps')

    session.request('POST', 'http://foo.bar', json={'foo': 'bar'},
                    headers={
                        'content-type': 'application/json; charset="latin1"'
                    })

    dumps().encode.assert_called_once_with('latin1')


def test_request_json_headers(full_session):
    session, build_opener, opener, response = full_session

    session.request('POST', 'http://foo.bar', json={'foo': 'bar'},
                    headers={
                        'content-type': 'application/json; charset="latin1"'
                    })

    args, kwargs = opener.open.call_args
    request = args[0]

    assert request.method == 'POST'
    assert request.data == b'{"foo": "bar"}'
    ct = request.headers['Content-type']
    assert ct == 'application/json; charset="latin1"'


def test_request_unix_socket(full_session):
    session, build_opener, opener, response = full_session

    session.request('GET', 'http://foo.bar', unix_socket='/foo/bar')

    args, kwargs = build_opener.call_args
    h = [h for h in args if isinstance(h, UnixHTTPHandler)]
    assert len(h) == 1
    assert h[0]._unix_socket == '/foo/bar'


def test_request_timeout(full_session):
    session, build_opener, opener, response = full_session

    session.request('GET', 'http://foo.bar', timeout=1)

    args, kwargs = opener.open.call_args
    assert kwargs['timeout'] == 1


def test_request_response(full_session, monkeypatch):
    session, build_opener, opener, response = full_session

    session.request('GET', 'http://foo.bar')

    args, kwargs = opener.open.call_args
    response.call_args[1]['request'] = args[0]
