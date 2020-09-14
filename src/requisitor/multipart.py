import mimetypes
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
    for field, value in sorted(fields.items()):
        if isinstance(value, str):
            main_type = 'text'
            sub_type = 'plain'
            content = value
            file = None
        elif isinstance(value, Mapping):
            file = value.get('file')
            content = value.get('content')
            if not any((file, content)):
                raise ValueError(
                    'at least one of "file" or "content" must be provided'
                )

            mime = value.get('mime_type')
            if not mime:
                try:
                    mime = mimetypes.guess_type(
                        file or '',
                        strict=False
                    )[0] or 'application/octet-stream'
                except Exception:
                    mime = 'application/octet-stream'
            main_type, _, sub_type = mime.partition('/')
        else:
            raise TypeError(
                'value must be a str, or mapping, cannot be type %s' % (
                    value.__class__.__name__
                )
            )

        if not content and file:
            content = read_bytes(file)
        elif content:
            content = ensure_bytes(content)

        if is_binary_data(content[:1024]):
            part = MIMEApplication(content)
            del part['Content-Type']
            part.add_header(
                'Content-Type',
                '%s/%s' % (main_type, sub_type)
            )
        else:
            part = MIMENonMultipart(main_type, sub_type)
            part.set_payload(content)

        part.add_header('Content-Disposition', 'form-data')
        del part['MIME-Version']
        part.set_param(
            'name',
            field,
            header='Content-Disposition'
        )
        if file:
            part.set_param(
                'filename',
                get_filename(file),
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
