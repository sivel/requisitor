import io
from http.client import HTTPResponse

from requisitor.errors import HTTPError
from requisitor.headers import Headers


class Sock(io.BytesIO):
    def makefile(self, *args):
        return self


RESP = b'''HTTP/1.1 400 OK^M
Content-Type: application/json^M
Set-Cookie: foo^M
Set-Cookie: bar^M
Content-Length: 14^M
^M
{"foo": "bar"}
'''


def test_HTTPError():
    fp = HTTPResponse(
        Sock(RESP),
        method='GET',
        url='http://foo.bar'
    )
    fp.begin()
    e = HTTPError(
        'http://foo.bar',
        200,
        'OK',
        {'Foo': 'bar'},
        fp,
    )

    assert isinstance(e.hdrs, Headers)
    assert e.raw is fp
    assert hasattr(e, 'encoding')
