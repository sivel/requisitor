import gzip
import importlib
import io
import sys
from http.client import HTTPResponse
from urllib.request import Request

import pytest

from requisitor.response import GzipDecodedResponse
from requisitor.response import Response


class Sock(io.BytesIO):
    def makefile(self, *args):
        return self


RESP = b'''HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Set-Cookie: foo
Set-Cookie: bar
Content-Length: 14

{"foo": "bar"}
'''

GZIP_RESP = b'''HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Set-Cookie: foo
Set-Cookie: bar
Content-Encoding: gzip
Content-Length: 14

%s
''' % gzip.compress(b'{"foo": "bar"}')


@pytest.fixture
def response():
    r = HTTPResponse(
        Sock(RESP),
        method='GET',
        url='https://foo.bar/',
    )
    r.begin()
    req = Request('https://foo.bar/')
    return Response(r, req)


def test_Response__init__(response):
    assert response.getheader('set-cookie') == 'foo, bar'
    assert isinstance(response.raw, HTTPResponse)


def test_Response_read(response):
    with pytest.raises(AttributeError):
        response.read


def test_Response_attr_mapping(response):
    assert response.status_code == response.status


def test_Response_encoding(response):
    assert response.encoding == 'utf-8'
    response.encoding = 'latin1'
    assert response.encoding == 'latin1'


def test_Response_bytes(response):
    assert response.bytes == b'{"foo": "bar"}'
    assert response.bytes == b'{"foo": "bar"}'


def test_Response_text(response):
    assert response.text == '{"foo": "bar"}'
    response.encoding = None
    assert response.text == '{"foo": "bar"}'


def test_Response_json(response):
    assert response.json() == {"foo": "bar"}


def test_Response_set_stream():
    r = HTTPResponse(
        Sock(GZIP_RESP),
        method='GET',
        url='https://foo.bar/',
    )
    r.begin()
    req = Request('https://foo.bar/')
    response = Response(r, req)
    assert isinstance(response.raw, GzipDecodedResponse)


def test_GzipDecodedResponse(monkeypatch, mocker):
    monkeypatch.delitem(sys.modules, 'gzip')
    monkeypatch.delitem(sys.modules, 'requisitor.response')

    orig_import = __import__

    def _import(*args):
        if args[0] == 'gzip':
            raise ImportError
        return orig_import(*args)

    mocker.patch('builtins.__import__', _import)

    mod = importlib.import_module('requisitor.response')
    assert mod.gzip is None
    pytest.raises(NotImplementedError, mod.GzipDecodedResponse, None)
