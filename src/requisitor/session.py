import http.client
import http.cookiejar
import json as _json
import ssl
import urllib.request
from urllib.parse import urlparse

from .auth import validate_auth
from .handlers import HTTPErrorHandler
from .handlers import HTTPSClientAuthHandler
from .handlers import RedirectHandler
from .handlers import UnixHTTPHandler
from .headers import Headers
from .headers import normalize_headers
from .response import Response
from .sentinel import Sentinel
from .utils import update_url_params


def _validate_cert(value):
    if value in (None, Sentinel):
        return value
    elif isinstance(value, tuple) and len(value) == 2:
        return value
    raise TypeError


class Session:
    def __init__(self):
        self._auth = None
        self._cert = None
        self._headers = Headers()

        self.cookies = http.cookiejar.CookieJar()

        self.handlers = []
        self.params = {}
        self.unix_socket = None
        self.verify = True

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, value):
        self._auth = validate_auth(value)

    @property
    def cert(self):
        return self._cert

    @cert.setter
    def cert(self, value):
        self._cert = _validate_cert(value)

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = normalize_headers(value)

    def _fallback(self, value, fallback):
        if value is Sentinel:
            return fallback
        return value

    def _create_context(self, verify):
        context = ssl.create_default_context()
        if not verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        if verify and verify is not True:
            context.load_verify_locations(cafile=verify)

        return context

    def request(self, method, url, params=Sentinel, data=None,
                headers=Sentinel, cookies=Sentinel, files=None, auth=Sentinel,
                timeout=None, allow_redirects=True, verify=Sentinel,
                cert=Sentinel, json=Sentinel, unix_socket=Sentinel):

        if any((files,)):
            raise NotImplementedError

        if all((data, json)):
            raise TypeError('Cannot specify both "data" and "json"')

        _headers = self.headers.copy()
        _headers.update(headers or {})

        _params = self.params.copy()
        _params.update(params or {})

        auth = self._fallback(auth, self.auth)
        cert = _validate_cert(self._fallback(cert, self.cert)) or (None, None)
        cookies = self._fallback(cookies, self.cookies)
        unix_socket = self._fallback(unix_socket, self.unix_socket)
        verify = self._fallback(verify, self.verify)

        if json is not Sentinel:
            if 'content-type' not in _headers:
                _headers['content-type'] = 'application/json'
            encoding = _headers.get_param('charset', 'utf-8')
            data = _json.dumps(json).encode(encoding)

        https_kwargs = {
            'context': self._create_context(verify),
            'client_cert': cert[0],
            'client_key': cert[1],
            'unix_socket': unix_socket,
        }

        handlers = [
            HTTPSClientAuthHandler(**https_kwargs),
            RedirectHandler(allow_redirects=allow_redirects),
            HTTPErrorHandler,
            urllib.request.HTTPCookieProcessor(cookies),
        ]

        if unix_socket:
            handlers.append(UnixHTTPHandler(unix_socket))

        o = urlparse(url)
        if auth:
            auth_info = validate_auth(auth)(o)
            _headers.update(
                auth_info.get('headers', {})
            )
            handlers.extend(
                auth_info.get('handlers', [])
            )

        handlers.extend(self.handlers)

        opener = urllib.request.build_opener(*handlers)
        req = urllib.request.Request(
            update_url_params(o, _params),
            data=data or None,
            method=method,
            headers=_headers,
        )
        return Response(
            opener.open(
                req,
                timeout=timeout,
            ),
            request=req
        )

    def get(self, url, **kwargs):
        r"""Sends a GET request. Returns :class:`HTTPResponse` object.

        :arg url: URL to request
        :kwarg \*\*kwargs: Optional arguments that ``open`` takes.
        :returns: requisitor.response.Response
        """

        return self.request('GET', url, **kwargs)

    def options(self, url, **kwargs):
        r"""Sends a OPTIONS request. Returns :class:`HTTPResponse` object.

        :arg url: URL to request
        :kwarg \*\*kwargs: Optional arguments that ``open`` takes.
        :returns: requisitor.response.Response
        """

        return self.request('OPTIONS', url, **kwargs)

    def head(self, url, **kwargs):
        r"""Sends a HEAD request. Returns :class:`HTTPResponse` object.

        :arg url: URL to request
        :kwarg \*\*kwargs: Optional arguments that ``open`` takes.
        :returns: requisitor.response.Response
        """

        return self.request('HEAD', url, **kwargs)

    def post(self, url, data=None, **kwargs):
        r"""Sends a POST request. Returns :class:`HTTPResponse` object.

        :arg url: URL to request.
        :kwarg data: (optional) bytes, or file-like object to send in the body
            of the request.
        :kwarg \*\*kwargs: Optional arguments that ``open`` takes.
        :returns: requisitor.response.Response
        """

        return self.request('POST', url, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        r"""Sends a PUT request. Returns :class:`HTTPResponse` object.

        :arg url: URL to request.
        :kwarg data: (optional) bytes, or file-like object to send in the body
            of the request.
        :kwarg \*\*kwargs: Optional arguments that ``open`` takes.
        :returns: requisitor.response.Response
        """

        return self.request('PUT', url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        r"""Sends a PATCH request. Returns :class:`HTTPResponse` object.

        :arg url: URL to request.
        :kwarg data: (optional) bytes, or file-like object to send in the body
            of the request.
        :kwarg \*\*kwargs: Optional arguments that ``open`` takes.
        :returns: requisitor.response.Response
        """

        return self.request('PATCH', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        r"""Sends a DELETE request. Returns :class:`HTTPResponse` object.

        :arg url: URL to request
        :kwargs \*\*kwargs: Optional arguments that ``open`` takes.
        :returns: requisitor.response.Response
        """

        return self.request('DELETE', url, **kwargs)
