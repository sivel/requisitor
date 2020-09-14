import os
import pathlib
from email.message import Message

import pytest

from requisitor.multipart import Field
from requisitor.multipart import prepare_multipart


def test_prepare_multipart(request):
    fixture_boundary = b'===============9055186793967377464=='

    here = os.path.dirname(__file__)
    multipart = os.path.join(here, 'fixtures/multipart.txt')

    cacert = os.path.join(here, 'fixtures/cacert.pem')
    cakey = os.path.join(here, 'fixtures/cakey.pem')
    cacert_txt = open(os.path.join(here, 'fixtures/cacert.txt'), 'rb')
    request.addfinalizer(cacert_txt.close)
    png = pathlib.Path(here) / 'fixtures/1x1.png'
    fields = {
        'form_field_1': 'form_value_1',
        'form_field_2': {
            'content': 'form_value_2',
        },
        'form_field_3': {
            'content': '<html></html>',
            'mime_type': 'text/html',
        },
        'form_field_4': {
            'content': '{"foo": "bar"}',
            'mime_type': 'application/json',
        },
        'file1': {
            'content': 'file_content_1',
            'file': 'fake_file1.txt',
        },
        'file2': {
            'content': '<html></html>',
            'mime_type': 'text/html',
            'file': 'fake_file2.html',
        },
        'file3': Field(
            file='fake_file3.json',
            content='{"foo": "bar"}',
            main_type='application',
            sub_type='json',
        ),
        'file4': {
            'file': cacert,
            'mime_type': 'text/plain',
        },
        'file5': {
            'file': cakey,
        },
        'file6': {
            'file': cacert_txt,
        },
        'file7': {
            'file': png,
        },
    }

    content_type, b_data = prepare_multipart(fields)

    headers = Message()
    headers['content-type'] = content_type
    assert headers.get_content_type() == 'multipart/form-data'
    boundary = headers.get_boundary()
    assert boundary is not None

    with open(multipart, 'rb') as f:
        b_expected = f.read().replace(fixture_boundary, boundary.encode())

    # Depending on Python version, there may or may not be a trailing newline
    assert b_data.rstrip(b'\r\n') == b_expected.rstrip(b'\r\n')


def test_wrong_type():
    pytest.raises(TypeError, prepare_multipart, 'foo')
    pytest.raises(TypeError, prepare_multipart, {'foo': None})


def test_empty():
    pytest.raises(ValueError, prepare_multipart, {'foo': {}})


def test_unknown_mime(mocker):
    fields = {'foo': {'filename': 'foo.boom', 'content': 'foo'}}
    mocker.patch('mimetypes.guess_type', return_value=(None, None))
    content_type, b_data = prepare_multipart(fields)
    assert b'Content-Type: application/octet-stream' in b_data


def test_bad_mime(mocker):
    fields = {'foo': {'filename': 'foo.boom', 'content': 'foo'}}
    mocker.patch('mimetypes.guess_type', side_effect=TypeError)
    content_type, b_data = prepare_multipart(fields)
    assert b'Content-Type: application/octet-stream' in b_data
