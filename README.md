# ezReq
Easy HttpClient Wrapper of Requests.

## Usage
```py
from ezreq import EzReq

e = EzReq("https://httpbin.org")
e.get("/get").text
e.post("post").text  # Same as `e.post("/post").text`

# NOTE: when you want to try visit another site
# like visit 'https://google.com', the attributes
# of EzReq will be auto updated by itself.

e.get("https://google.com")
e._scheme    # -> 'https'
e._base_url  # -> 'https://google.com'
```

# Supported Method
- get(url, \*\*kwargs)
- post(url, \*\*kwargs)

# Add Custom Method
```py
from ezreq import EzReq
from ezreq import normalize_url

# Override the EzReq
class MyEzReq(EzReq):
  ...
  @normalize_url
  def put(url, data=None, **kwargs):
    return self._session.put(url, data=data, **kwargs)
...
```

# EzReq Shortcuts(constructor only)
- `kwargs["headers"]` -> `Session.headers`
- `kwargs["max_retries"]` -> `Session.<adapter>.max_retires`

# Features & Notice
When each method be called, the `self._headers` which binds on `self._session.headers` its
`referer` and `origin` will be auto updated. Your custom method(s) has both of the these,
so you should manually delete the which one you not need.


For Example:
```py
  @normalize_url
  def get(self, url, **kwargs):
    # get method doesn't need headers["origin"]
    self._headers.pop("origin")
    return self._session.get(url, **kwargs)
```
