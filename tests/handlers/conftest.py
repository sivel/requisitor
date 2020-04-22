import io
from http.client import HTTPResponse

import pytest

from requisitor.codes import codes


class Sock(io.BytesIO):
    def makefile(self, *args):
        return self


RESP = b'''HTTP/1.1 %d %s
Content-Type: application/json; charset=utf-8
Foo: bar
Baz: qux
Content-Length: 14
Location: %s

{"foo": "bar"}
'''


@pytest.fixture
def response():
    def inner(code, location):
        r = HTTPResponse(
            Sock(RESP % (code, codes[code].encode(), location.encode())),
            method='GET',
            url='https://foo.bar/',
        )
        r.begin()
        return r
    return inner
