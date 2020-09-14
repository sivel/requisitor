# -*- coding: utf-8 -*-
# Copyright 2020 Matt Martz
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import io
import json
from functools import partial

from .headers import normalize_headers

try:
    import gzip
except ImportError:
    gzip = None


class GzipDecodedResponse(gzip.GzipFile if gzip else object):
    """A file-like object to decode a response encoded with the gzip
        method, as described in RFC 1952.

        Largely copied from ``xmlrpclib``/``xmlrpc.client``
        """
    def __init__(self, response):
        if not gzip:
            raise NotImplementedError

        # response doesn't support tell() and read(), required by
        # GzipFile
        self.io = io.BytesIO()
        for block in iter(partial(response.read, 1024), b''):
            self.io.write(block)
        self.io.seek(0)
        gzip.GzipFile.__init__(self, mode='rb', fileobj=self.io)

    def close(self):
        try:
            gzip.GzipFile.close(self)
        finally:
            self.io.close()


class Response:
    _attr_map = {
        'status_code': 'status',
    }

    def __init__(self, response, request=None, _error=False):

        self._response = response
        if _error:
            self.response = self._response
            self.headers = normalize_headers(self.headers)
        else:
            response.headers = normalize_headers(response.headers)
        self.request = request

        self._set_stream(response)

        self._bytes = None
        self._encoding = None

    def __getattr__(self, name):
        if name == 'read':
            raise AttributeError

        return getattr(
            self._response,
            Response._attr_map.get(name, name)
        )

    def _set_stream(self, stream):
        if self.headers.get('content-encoding', '') == 'gzip':
            self.raw = stream.fp = GzipDecodedResponse(stream)
        else:
            self.raw = stream

    @property
    def encoding(self):
        if self._encoding:
            return self._encoding

        return self.headers.get_param('charset')

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    @property
    def bytes(self):
        if self._bytes:
            return self._bytes

        self._bytes = self.raw.read()
        return self._bytes

    @property
    def text(self):
        encoding = self.encoding or 'utf-8'
        return self.bytes.decode(encoding)

    def json(self):
        return json.loads(self.text)
