from urllib.parse import urlparse
from urllib.request import HTTPDigestAuthHandler

import pytest

from requisitor.auth import HTTPBasicAuth
from requisitor.auth import HTTPDigestAuth
from requisitor.auth import validate_auth


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (('user', 'pass'), HTTPBasicAuth),
        (HTTPBasicAuth('user', 'pass'), HTTPBasicAuth),
        (HTTPDigestAuth('user', 'pass'), HTTPDigestAuth),
    ]
)
def test_validate_auth(test_input, expected):
    assert isinstance(validate_auth(test_input), expected)

    assert validate_auth(None) is None
    pytest.raises(TypeError, validate_auth, '')
    pytest.raises(TypeError, validate_auth, ())


def test_HTTPBasicAuth():
    expected = {
        'headers': {
            'Authorization': 'Basic dXNlcjpwYXNz'
        }
    }
    assert HTTPBasicAuth('user', 'pass')(None) == expected


def test_HTTPDigestAuth():
    assert isinstance(
        HTTPDigestAuth('user', 'pass')(urlparse(''))['handlers'][0],
        HTTPDigestAuthHandler
    )
