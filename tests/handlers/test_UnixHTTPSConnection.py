from requisitor.handlers import UnixHTTPSConnection


def test_connect(mocker):
    httpsconn = mocker.patch('http.client.HTTPSConnection.connect')
    httpconn = mocker.patch('http.client.HTTPConnection.connect')

    conn = UnixHTTPSConnection('foo')
    conn('host').connect()

    httpsconn.assert_called()
    httpconn.assert_not_called()


def test_call(mocker):
    init = mocker.patch('http.client.HTTPSConnection.__init__')
    conn = UnixHTTPSConnection('foo')
    assert conn('host') is conn
    init.assert_called_once()
