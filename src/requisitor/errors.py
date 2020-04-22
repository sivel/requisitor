import urllib.error

from .response import Response


class HTTPError(urllib.error.HTTPError, Response):
    def __init__(self, url, code, msg, hdrs, fp, req=None):
        super(HTTPError, self).__init__(url, code, msg, hdrs, fp)
        Response.__init__(self, fp, req, _error=True)