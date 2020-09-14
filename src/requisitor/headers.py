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

import http.client

from .sentinel import Sentinel


class Headers(http.client.HTTPMessage):
    def __repr__(self):
        return repr(dict(self))

    def copy(self):
        headers = Headers()
        headers.update(self)
        return headers

    def pop(self, key, default=Sentinel):
        value = self.get(key, default)
        if value is Sentinel:
            raise KeyError(key)
        del self[key]
        return value

    def update(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('update expected at most 1 arguments, got %d' %
                            len(args))

        items = []
        if args:
            other = args[0]
            if isinstance(other, (dict, http.client.HTTPMessage)):
                items[:] = other.items()
            elif isinstance(other, list):
                items[:] = other
            else:
                raise TypeError
        for obj in (items, kwds.items()):
            for name, value in obj:
                self.pop(name, None)
                self[name] = value

    def add_header(self, name, value, **params):
        orig = self.pop(name, None)
        super(Headers, self).add_header(name, value, **params)
        if orig:
            new = self.pop(name)
            self[name] = '{}, {}'.format(orig, new)


def normalize_headers(headers):
    normalized = Headers()

    if isinstance(headers, (dict, http.client.HTTPMessage)):
        items = headers.items()
    elif isinstance(headers, list):
        items = headers
    else:
        raise TypeError

    # Don't be lossy, append header values for duplicate headers
    for name, value in items:
        if name in normalized:
            old = normalized[name]
            del normalized[name]
            normalized[name] = ', '.join((old, value))
        else:
            normalized[name] = value

    return normalized
