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

import urllib.parse


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
