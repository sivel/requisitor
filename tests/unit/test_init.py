import pytest

import requisitor


@pytest.fixture
def session(mocker):
    return mocker.patch('requisitor.Session')


def test_get(session):
    requisitor.get('http://foo.bar/', headers={})

    session().get.assert_called_once_with('http://foo.bar/', headers={})


def test_options(session):
    requisitor.options('http://foo.bar/', headers={})

    session().options.assert_called_once_with('http://foo.bar/', headers={})


def test_head(session):
    requisitor.head('http://foo.bar/', headers={})

    session().head.assert_called_once_with('http://foo.bar/', headers={})


def test_post(session):
    requisitor.post('http://foo.bar/', data='baz', headers={})

    session().post.assert_called_once_with('http://foo.bar/', data='baz',
                                           headers={})


def test_put(session):
    requisitor.put('http://foo.bar/', data='baz', headers={})

    session().put.assert_called_once_with('http://foo.bar/', data='baz',
                                          headers={})


def test_patch(session):
    requisitor.patch('http://foo.bar/', data='baz', headers={})

    session().patch.assert_called_once_with('http://foo.bar/', data='baz',
                                            headers={})


def test_delete(session):
    requisitor.delete('http://foo.bar/', headers={})

    session().delete.assert_called_once_with('http://foo.bar/', headers={})
