from urllib.error import HTTPError as UrllibHTTPError

import pytest

from requisitor.errors import HTTPError
from requisitor.session import Session


def test_HTTPErrorHandler(response, mocker):
    r = response(400, '')

    mocker.patch('http.client.HTTPConnection.request')
    mocker.patch('http.client.HTTPConnection.getresponse', return_value=r)

    s = Session()
    excinfo = pytest.raises(HTTPError, s.request, 'GET', 'http://foo.bar')
    assert excinfo.type is HTTPError
    assert excinfo.type is not UrllibHTTPError
