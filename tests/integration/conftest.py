import ast
import os
from urllib.parse import urlparse

import pytest

use_ssl = '_UNSET'


@pytest.fixture
def httpbin():
    def inner(url, scheme):
        o = urlparse(url)
        netloc = os.getenv('HTTPBIN', 'httpbin.org')
        n = o._replace(scheme=scheme, netloc=netloc)
        return n.geturl()
    return inner


@pytest.fixture
def skip_ssl():
    global use_ssl
    if use_ssl == '_UNSET':
        use_ssl = ast.literal_eval(os.getenv('HTTPBIN_SSL', 'True') or 'False')
    if not use_ssl:
        pytest.skip('httpbin does not support ssl')
