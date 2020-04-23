from urllib.parse import urlparse

import pytest

from requisitor.utils import update_url_params


@pytest.mark.parametrize(
    'url,params,expected',
    [
        ('http://foo.bar', {}, 'http://foo.bar'),
        ('http://foo.bar?a=b', {'a': 'c'}, 'http://foo.bar?a=c'),
        ('http://foo.bar?a=b', {'c': 'd'}, 'http://foo.bar?a=b&c=d'),
        ('http://foo.bar', {'a': 'b'}, 'http://foo.bar?a=b'),
        (urlparse('http://foo.bar'), {}, 'http://foo.bar'),
        (urlparse('http://foo.bar?a=b'), {'a': 'c'}, 'http://foo.bar?a=c'),
        (urlparse('http://foo.bar?a=b'), {'c': 'd'}, 'http://foo.bar?a=b&c=d'),
        (urlparse('http://foo.bar'), {'a': 'b'}, 'http://foo.bar?a=b'),
    ]
)
def test_update_url_params(url, params, expected):
    assert update_url_params(url, params) == expected
