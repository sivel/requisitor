import io
import os
import pathlib
from urllib.parse import urlparse

import pytest

from requisitor.utils import ensure_bytes
from requisitor.utils import get_filename
from requisitor.utils import is_binary_data
from requisitor.utils import is_binary_fileobj
from requisitor.utils import read_bytes
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


def test_is_binary_data():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'fixtures/1x1.png'), 'rb') as f:
        data = f.read()

    assert is_binary_data(data) is True
    assert is_binary_data(b'foo') is False
    with pytest.raises(TypeError):
        is_binary_data('foo')


def test_is_binary_fileobj():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'fixtures/1x1.png'), 'rb') as f:
        assert is_binary_fileobj(f) is True

    with open(os.path.join(here, 'fixtures/1x1.png'), 'r') as f:
        assert is_binary_fileobj(f) is False

    assert is_binary_fileobj('foo') is False

    assert is_binary_fileobj(io.BytesIO()) is True
    assert is_binary_fileobj(io.StringIO()) is False


def test_get_filename():
    here = os.path.dirname(__file__)
    png = os.path.join(here, 'fixtures/1x1.png')
    with open(png, 'rb') as f:
        assert get_filename(f) == '1x1.png'
        assert get_filename(f, basename=False) == png

    png_pathlib = pathlib.Path(here) / 'fixtures' / '1x1.png'

    assert get_filename(png_pathlib) == '1x1.png'
    assert get_filename(png_pathlib, False) == png

    assert get_filename(png) == '1x1.png'
    assert get_filename(png, False) == png

    with pytest.raises(TypeError):
        get_filename(True)

    with pytest.raises(TypeError), open(png, 'r') as f:
        get_filename(f)


def test_read_bytes():
    here = os.path.dirname(__file__)
    small = os.path.join(here, 'fixtures/small.txt')
    small_pathlib = pathlib.Path(here) / 'fixtures' / 'small.txt'

    expected = b'foo\n'

    with open(small, 'rb') as f:
        assert read_bytes(f) == expected

    assert read_bytes(small_pathlib) == expected
    assert read_bytes(small) == expected

    with pytest.raises(TypeError), open(small, 'r') as f:
        assert read_bytes(f)


def test_ensure_bytes():
    assert ensure_bytes('foo') == b'foo'
    assert ensure_bytes(b'foo') == b'foo'
