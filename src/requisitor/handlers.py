# -*- coding: utf-8 -*-
# Copyright 2020 Matt Martz

import contextlib
import http.client
import socket
import urllib.error
import urllib.request
import urllib.response

from .errors import HTTPError
from .response import Response


class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allow_redirects=True):
        self.allow_redirects = allow_redirects

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not self.allow_redirects:
            raise HTTPError(newurl, code, msg, headers, fp, req)

        m = req.get_method()
        if code not in (301, 302, 303, 307, 308):
            raise HTTPError(req.full_url, code, msg, headers, fp, req)

        data = req.data
        origin_req_host = req.origin_req_host

        # Be conciliant with URIs containing a space.  This is mainly
        # redundant with the more complete encoding done in http_error_302,
        # but it is kept for compatibility with other callers.
        newurl = newurl.replace(' ', '%20')

        # Suport redirect with payload and original headers
        if code in (307, 308):
            # Preserve payload and headers
            newheaders = req.headers
        else:
            # Do not preserve payload and filter headers
            data = None

            CONTENT_HEADERS = ('content-length', 'content-type')
            newheaders = {k: v for k, v in req.headers.items()
                          if k.lower() not in CONTENT_HEADERS}

            # http://tools.ietf.org/html/rfc7231#section-6.4.4
            if code == 303 and m != 'HEAD':
                m = 'GET'

            # Non-standard transformations

            # Turn 302s into GETs.
            if code == 302 and m != 'HEAD':
                m = 'GET'

            # Turn 301 from POST into GET
            if code == 301 and m == 'POST':
                m = 'GET'

        return urllib.request.Request(
            newurl,
            method=m,
            headers=newheaders,
            data=data,
            origin_req_host=origin_req_host,
            unverifiable=True
        )

    def http_error_302(self, req, fp, code, msg, headers):
        try:
            return super(RedirectHandler, self).http_error_302(
                req,
                fp,
                code,
                msg,
                headers
            )
        except HTTPError:
            urllib.response.addinfourl(fp, headers, req.full_url, code=code)
            return Response(
                fp,
                request=req
            )

    http_error_301 = http_error_303 = http_error_302
    http_error_307 = http_error_308 = http_error_302


class HTTPErrorHandler(urllib.request.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, hdrs):
        raise HTTPError(req.full_url, code, msg, hdrs, fp, req)


class HTTPSClientAuthHandler(urllib.request.HTTPSHandler):
    '''Handles client authentication via cert/key

    This is a fairly lightweight extension on HTTPSHandler, and can be used
    in place of HTTPSHandler
    '''

    def __init__(self, client_cert=None, client_key=None, unix_socket=None,
                 **kwargs):
        urllib.request.HTTPSHandler.__init__(self, **kwargs)
        self.client_cert = client_cert
        self.client_key = client_key
        self._unix_socket = unix_socket

    def https_open(self, req):
        return self.do_open(self._build_https_connection, req)

    def _build_https_connection(self, host, **kwargs):
        kwargs.update({
            'cert_file': self.client_cert,
            'key_file': self.client_key,
            'context': self._context,
        })
        if self._unix_socket:
            return UnixHTTPSConnection(self._unix_socket)(host, **kwargs)
        return http.client.HTTPSConnection(host, **kwargs)


@contextlib.contextmanager
def unix_socket_patch_httpconnection_connect():
    '''Monkey patch ``http.client.HTTPConnection.connect`` to be
    ``UnixHTTPConnection.connect`` so that when calling
    ``super(UnixHTTPSConnection, self).connect()`` we get the
    correct behavior of creating self.sock for the unix socket
    '''
    _connect = http.client.HTTPConnection.connect
    http.client.HTTPConnection.connect = UnixHTTPConnection.connect
    yield
    http.client.HTTPConnection.connect = _connect


class UnixHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, unix_socket):
        self._unix_socket = unix_socket

    def connect(self):
        # This method exists simply to ensure we monkeypatch
        # http.client.HTTPConnection.connect to call UnixHTTPConnection.connect
        with unix_socket_patch_httpconnection_connect():
            super(UnixHTTPSConnection, self).connect()

    def __call__(self, *args, **kwargs):
        http.client.HTTPSConnection.__init__(self, *args, **kwargs)
        return self


class UnixHTTPConnection(http.client.HTTPConnection):
    '''Handles http requests to a unix socket file'''

    def __init__(self, unix_socket):
        self._unix_socket = unix_socket

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.sock.connect(self._unix_socket)
        except OSError as e:
            raise OSError(
                'Invalid Socket File (%s): %s' % (self._unix_socket, e)
            )
        if self.timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
            self.sock.settimeout(self.timeout)

    def __call__(self, *args, **kwargs):
        http.client.HTTPConnection.__init__(self, *args, **kwargs)
        return self


class UnixHTTPHandler(urllib.request.HTTPHandler):
    '''Handler for Unix urls'''

    def __init__(self, unix_socket, **kwargs):
        urllib.request.HTTPHandler.__init__(self, **kwargs)
        self._unix_socket = unix_socket

    def http_open(self, req):
        return self.do_open(UnixHTTPConnection(self._unix_socket), req)
