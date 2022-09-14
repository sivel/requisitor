# -*- coding: utf-8 -*-
# Copyright 2020 Matt Martz

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
