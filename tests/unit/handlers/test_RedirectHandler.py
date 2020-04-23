from unittest.mock import MagicMock
from urllib.request import Request

import pytest

from requisitor.codes import codes
from requisitor.errors import HTTPError
from requisitor.handlers import RedirectHandler
from requisitor.response import Response


def test_no_redirects(response):
    r = response(200, 'https://foo.bar/')
    req = Request('http://foo.bar')

    h = RedirectHandler(allow_redirects=False)

    with pytest.raises(HTTPError):
        h.redirect_request(
            req,
            r,
            302,
            'Found',
            r.headers,
            'http://foo.bar/baz'
        )


def test_codes(response):
    h = RedirectHandler()
    req = Request('http://foo.bar', method='POST', data=b'foo')
    for code in (301, 302, 303):
        r = response(code, 'https://foo.bar/baz')
        newreq = h.redirect_request(
            req,
            r,
            code,
            codes[code],
            r.headers,
            'http://foo.bar/baz'
        )
        assert newreq.get_method() in ('GET', 'HEAD')
        assert newreq.data is None

    req = Request('http://foo.bar', method='POST', data=b'foo')
    for code in (307, 308):
        r = response(code, 'https://foo.bar/baz')
        newreq = h.redirect_request(
            req,
            r,
            code,
            codes[code],
            r.headers,
            'http://foo.bar/baz'
        )
        assert newreq.get_method() == 'POST'
        assert newreq.data == b'foo'

    req = Request('http://foo.bar', method='POST', data=b'foo')
    r = response(400, 'https://foo.bar/baz')

    with pytest.raises(HTTPError):
        h.redirect_request(
            req,
            r,
            400,
            codes[400],
            r.headers,
            'http://foo.bar/baz'
        )


def test_http_error_302(response, monkeypatch):
    h = RedirectHandler()
    h.parent = MagicMock()
    req = Request('http://foo.bar', method='POST', data=b'foo')
    req.timeout = None
    for code in (301, 302, 303, 307, 308):
        r = response(code, 'https://foo.bar/baz')
        new_r = getattr(h, 'http_error_%s' % code)(
            req,
            r,
            200,
            codes[200],
            r.headers,
        )

        assert isinstance(new_r, Response)
