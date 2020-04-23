import requisitor


def test_get_http(httpbin):
    url = httpbin('/get', 'http')
    r = requisitor.get(
        url,
        params={'foo': 'bar'},
        headers={'bar': 'baz'},
    )

    data = r.json()
    assert data['args'] == {'foo': 'bar'}
    assert data['headers']['Bar'] == 'baz'
    assert data['url'] == httpbin('/get?foo=bar', 'http')


def test_get_https(httpbin, skip_ssl):
    url = httpbin('/get', 'https')
    r = requisitor.get(
        url,
        params={'foo': 'bar'},
        headers={'bar': 'baz'},
    )

    data = r.json()
    assert data['args'] == {'foo': 'bar'}
    assert data['headers']['Bar'] == 'baz'
    assert data['url'] == httpbin('/get?foo=bar', 'https')
