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

from .session import Session


def get(url, **kwargs):
    r"""Sends a GET request. Returns :class:`HTTPResponse` object.

    :arg url: URL to request
    :kwarg \*\*kwargs: Optional arguments that ``Session.request`` takes.
    :returns: requisitor.response.Response
    """

    return Session().get(url, **kwargs)


def options(url, **kwargs):
    r"""Sends a OPTIONS request. Returns :class:`HTTPResponse` object.

    :arg url: URL to request
    :kwarg \*\*kwargs: Optional arguments that ``Session.request`` takes.
    :returns: requisitor.response.Response
    """

    return Session().options(url, **kwargs)


def head(url, **kwargs):
    r"""Sends a HEAD request. Returns :class:`HTTPResponse` object.

    :arg url: URL to request
    :kwarg \*\*kwargs: Optional arguments that ``Session.request`` takes.
    :returns: requisitor.response.Response
    """

    return Session().head(url, **kwargs)


def post(url, data=None, **kwargs):
    r"""Sends a POST request. Returns :class:`HTTPResponse` object.

    :arg url: URL to request.
    :kwarg data: (optional) bytes, or file-like object to send in the body
        of the request.
    :kwarg \*\*kwargs: Optional arguments that ``Session.request`` takes.
    :returns: requisitor.response.Response
    """

    return Session().post(url, data=data, **kwargs)


def put(url, data=None, **kwargs):
    r"""Sends a PUT request. Returns :class:`HTTPResponse` object.

    :arg url: URL to request.
    :kwarg data: (optional) bytes, or file-like object to send in the body
        of the request.
    :kwarg \*\*kwargs: Optional arguments that ``Session.request`` takes.
    :returns: requisitor.response.Response
    """

    return Session().put(url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    r"""Sends a PATCH request. Returns :class:`HTTPResponse` object.

    :arg url: URL to request.
    :kwarg data: (optional) bytes, or file-like object to send in the body
        of the request.
    :kwarg \*\*kwargs: Optional arguments that ``Session.request`` takes.
    :returns: requisitor.response.Response
    """

    return Session().patch(url, data=data, **kwargs)


def delete(url, **kwargs):
    r"""Sends a DELETE request. Returns :class:`HTTPResponse` object.

    :arg url: URL to request
    :kwargs \*\*kwargs: Optional arguments that ``Session.request`` takes.
    :returns: requisitor.response.Response
    """

    return Session().delete(url, **kwargs)
