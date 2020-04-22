import http.client

from .sentinel import Sentinel


class Headers(http.client.HTTPMessage):
    def __repr__(self):
        return repr(dict(self))

    def copy(self):
        headers = Headers()
        headers.update(self)
        return headers

    def pop(self, key, default=Sentinel):
        value = self.get(key, default)
        if value is Sentinel:
            raise KeyError(key)
        del self[key]
        return value

    def update(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('update expected at most 1 arguments, got %d' %
                            len(args))

        items = []
        if args:
            other = args[0]
            if isinstance(other, (dict, http.client.HTTPMessage)):
                items[:] = other.items()
            elif isinstance(other, list):
                items[:] = other
            else:
                raise TypeError
        for obj in (items, kwds.items()):
            for name, value in obj:
                self.pop(name, None)
                self[name] = value

    def add_header(self, name, value, **params):
        orig = self.pop(name, None)
        super(Headers, self).add_header(name, value, **params)
        if orig:
            new = self.pop(name)
            self[name] = '{}, {}'.format(orig, new)


def normalize_headers(headers):
    normalized = Headers()

    if isinstance(headers, (dict, http.client.HTTPMessage)):
        items = headers.items()
    elif isinstance(headers, list):
        items = headers
    else:
        raise TypeError

    # Don't be lossy, append header values for duplicate headers
    for name, value in items:
        if name in normalized:
            old = normalized[name]
            del normalized[name]
            normalized[name] = ', '.join((old, value))
        else:
            normalized[name] = value

    return normalized
