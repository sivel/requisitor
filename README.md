# requisitor

![](https://github.com/sivel/requisitor/workflows/CI/badge.svg?branch=master)

Simple HTTP library utilizing only Python stdlib

## Examples

```pycon
>>> r = requisitor.get('http://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
>>> r.headers['content-type']
'application/json'
>>> r.text
'{\n  "authenticated": true, \n  "user": "user"\n}\n'
>>> r.json()
{'authenticated': True, 'user': 'user'}
>>>
```
