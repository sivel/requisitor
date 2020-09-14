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

import urllib.error

from .response import Response


class HTTPError(urllib.error.HTTPError, Response):
    def __init__(self, url, code, msg, hdrs, fp, req=None):
        super(HTTPError, self).__init__(url, code, msg, hdrs, fp)
        Response.__init__(self, fp, req, _error=True)
