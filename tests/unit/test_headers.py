from http.client import HTTPMessage

import pytest

from requisitor.headers import Headers
from requisitor.headers import normalize_headers


def test_Headers_repr():
    assert repr(Headers()) == '{}'


def test_Headers_copy():
    orig = Headers()
    orig['Foo'] = 'bar'
    copy = orig.copy()

    assert copy is not orig
    assert orig['foo'] == copy['foo']

    orig['foo'] = 'baz'

    assert copy['foo'] == 'bar'


def test_Headers_update_TypeError():
    h = Headers()
    pytest.raises(TypeError, h.update, None, None)
    pytest.raises(TypeError, h.update, None)


def test_Headers_update_dict():
    h = Headers()
    h['foo'] = 'bar'
    h.update({'foo': 'baz'})
    assert h['foo'] == 'baz'


def test_Headers_update_list():
    h = Headers()
    h['foo'] = 'bar'
    h.update([('foo', 'baz')])
    assert h['foo'] == 'baz'


def test_Headers_update_kwargs():
    h = Headers()
    h['foo'] = 'bar'
    h.update(foo='baz')
    assert h['foo'] == 'baz'


def test_Headers_update_args_kwargs():
    h = Headers()
    h['foo'] = 'bar'
    h.update({'foo': 'baz'}, foo='qux')
    assert h['foo'] == 'qux'


def test_Headers_pop():
    h = Headers()
    pytest.raises(KeyError, h.pop, 'foo')
    assert h.pop('foo', None) is None
    h['foo'] = 'bar'
    assert h.pop('foo') == 'bar'
    pytest.raises(KeyError, h.pop, 'foo')


def test_Headers_add_header():
    h = Headers()
    h.add_header('Cookie', 'foo')
    assert len(h) == 1
    assert h['cookie'] == 'foo'
    h.add_header('Cookie', 'bar')
    assert len(h) == 1
    assert h['cookie'] == 'foo, bar'


def test_normalize_headers_list_dupes():
    headers = [
        ('Cookie', 'foo'),
        ('Cookie', 'bar')
    ]

    new = normalize_headers(headers)
    assert len(new) == 1
    assert new['cookie'] == 'foo, bar'


def test_normalize_headers_message_dupes():
    headers = HTTPMessage()
    headers.add_header('Cookie', 'foo')
    headers.add_header('Cookie', 'bar')

    new = normalize_headers(headers)
    assert len(new) == 1
    assert new['cookie'] == 'foo, bar'


def test_normalize_headers_TypeError():
    pytest.raises(TypeError, normalize_headers, None)


def test_normalize_headers():
    headers = {
        'Cookie': 'foo',
        'Bar': 'baz'
    }
    new = normalize_headers(headers)
    assert len(new) == 2
    assert new['cookie'] == 'foo'
    assert new['bar'] == 'baz'
