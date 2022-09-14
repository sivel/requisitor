# -*- coding: utf-8 -*-
# Copyright 2020 Matt Martz

import mimetypes
from collections import namedtuple
from collections.abc import Mapping
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.parser import BytesHeaderParser
from email.policy import HTTP

from .utils import ensure_bytes
from .utils import get_filename
from .utils import is_binary_data
from .utils import read_bytes


Field = namedtuple('Field', ('file', 'content', 'main_type', 'sub_type'))


def _parse_field(field):
    if isinstance(field, Field):
        return field
    elif isinstance(field, str):
        return Field(None, field, 'text', 'plain')
    elif isinstance(field, Mapping):
        file = field.get('file')
        content = field.get('content')
        if not any((file, content)):
            raise ValueError(
                'at least one of "file" or "content" must be provided'
            )

        mime = field.get('mime_type')
        if not mime:
            if not file or isinstance(file, str):
                url = file
            else:
                url = get_filename(file)
            try:
                mime = mimetypes.guess_type(
                    url or '',
                    strict=False
                )[0] or 'application/octet-stream'
            except Exception:
                mime = 'application/octet-stream'
        main_type, _, sub_type = mime.partition('/')
        return Field(file, content, main_type, sub_type)
    else:
        raise TypeError(
            'value must be Field, str, or mapping, cannot be type %s' % (
                field.__class__.__name__
            )
        )


def prepare_multipart(fields):
    """Takes a mapping, and prepares a multipart/form-data body

    :arg fields: Mapping
    :returns: tuple of (content_type, body) where ``content_type`` is
        the ``multipart/form-data`` ``Content-Type`` header including
        ``boundary`` and ``body`` is the prepared bytestring body

    Payload content from a file will be base64 encoded and will include
    the appropriate ``Content-Transfer-Encoding`` and ``Content-Type``
    headers.

    Example:
        {
            "file1": {
                "file": "/bin/true",
                "mime_type": "application/octet-stream"
            },
            "file2": {
                "content": "text based file content",
                "file": "fake.txt",
                "mime_type": "text/plain",
            },
            "text_form_field": "value"
        }
    """

    if not isinstance(fields, Mapping):
        raise TypeError(
            'Mapping is required, cannot be type %s' % (
                fields.__class__.__name__
            )
        )

    m = MIMEMultipart('form-data')
    for field_name in sorted(fields):
        field = _parse_field(fields[field_name])

        if not field.content and field.file:
            content = read_bytes(field.file)
        else:
            content = ensure_bytes(field.content)

        if is_binary_data(content[:1024]):
            part = MIMEApplication(content)
            del part['Content-Type']
            part.add_header(
                'Content-Type',
                '%s/%s' % (field.main_type, field.sub_type)
            )
        else:
            part = MIMENonMultipart(field.main_type, field.sub_type)
            part.set_payload(content)

        part.add_header('Content-Disposition', 'form-data')
        del part['MIME-Version']
        part.set_param(
            'name',
            field_name,
            header='Content-Disposition'
        )
        if field.file:
            part.set_param(
                'filename',
                get_filename(field.file),
                header='Content-Disposition'
            )

        m.attach(part)

    data = m.as_bytes(policy=HTTP)
    del m

    headers, _, content = data.partition(b'\r\n\r\n')
    del data

    parser = BytesHeaderParser().parsebytes
    return (
        parser(headers)['content-type'],
        content
    )
