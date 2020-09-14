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

import base64
import urllib.request


def validate_auth(value):
    if value is None:
        return value
    elif isinstance(value, tuple):
        if len(value) != 2:
            raise TypeError
        return HTTPBasicAuth(*value)
    elif isinstance(value, HTTPAuth):
        return value

    raise TypeError


class HTTPAuth:
    def __init__(self, user, password):
        self.user = user
        self.password = password


class HTTPBasicAuth(HTTPAuth):
    def __call__(self, parsed_url):
        return {
            'headers': {
                'Authorization': 'Basic {}'.format(
                    base64.b64encode(
                        '{}:{}'.format(
                            self.user,
                            self.password
                        ).encode()
                    ).decode()
                ),
            }
        }


class HTTPDigestAuth(HTTPAuth):
    def __call__(self, parsed_url):
        pwd_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pwd_mgr.add_password(None, parsed_url.netloc, self.user, self.password)

        return {
            'handlers': [
                urllib.request.HTTPDigestAuthHandler(pwd_mgr),
            ]
        }
