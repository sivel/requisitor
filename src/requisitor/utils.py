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
import pathlib
import urllib.parse

TEXTCHARS = bytearray(
    {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f}
)


def update_url_params(url, params):
    if isinstance(url, urllib.parse.ParseResult):
        o = url
    else:
        o = urllib.parse.urlparse(url)
    _params = {
        **urllib.parse.parse_qs(o.query),
        **{k: v for k, v in params.items() if v is not None}
    }
    new = o._replace(
        query=urllib.parse.urlencode(
            _params,
            doseq=True
        )
    )
    return new.geturl()


def is_binary_data(data):
    if not isinstance(data, bytes):
        raise TypeError(
            'value must be a bytes, cannot be type %s' % (
                data.__class__.__name__
            )
        )
    return bool(
        data.translate(None, TEXTCHARS)
    )


def is_binary_fileobj(obj):
    return isinstance(obj, (io.RawIOBase, io.BufferedIOBase))


def get_filename(obj):
    if is_binary_fileobj(obj) or isinstance(obj, pathlib.Path):
        return obj.name
    elif isinstance(obj, str):
        return obj
    else:
        raise TypeError(
            'value must be a str, pathlib.Path, or binary file object, '
            'cannot be type %s' % (
                obj.__class__.__name__
            )
        )


def read_bytes(obj):
    if is_binary_fileobj(obj):
        return obj.read()
    elif isinstance(obj, pathlib.Path):
        return obj.read_bytes()
    elif isinstance(obj, str):
        return pathlib.Path(obj).read_bytes()
    else:
        raise TypeError(
            'value must be a str, pathlib.Path, or binary file object, '
            'cannot be type %s' % (
                obj.__class__.__name__
            )
        )


def ensure_bytes(obj, encoding=None):
    if isinstance(obj, bytes):
        return obj
    return obj.encode(encoding)
