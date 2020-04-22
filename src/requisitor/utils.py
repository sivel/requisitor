import urllib.parse


def update_url_params(url, params):
    if isinstance(url, urllib.parse.ParseResult):
        o = url
    else:
        o = urllib.parse.urlparse(url)
    _params = {
        **urllib.parse.parse_qs(o.query),
        **{k: v for k, v in params.items() if v is not None}
    }
    new = o._replace(
        query=urllib.parse.urlencode(
            _params,
            doseq=True
        )
    )
    return new.geturl()
