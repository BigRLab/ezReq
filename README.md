# ezReq
Easy HttpClient Component for Python.

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
e._protocol  # -> 'https:'
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

# EzReq Shortcuts
- `kwargs["headers"]` -> `Session.headers`
- `kwargs["max_retries"]` -> `Session.<adapter>.max_retires`

