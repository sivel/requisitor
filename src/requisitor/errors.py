# -*- coding: utf-8 -*-
# Copyright 2020 Matt Martz

import urllib.error

from .response import Response


class HTTPError(urllib.error.HTTPError, Response):
    def __init__(self, url, code, msg, hdrs, fp, req=None):
        super().__init__(url, code, msg, hdrs, fp)
        Response.__init__(self, fp, req, _error=True)
