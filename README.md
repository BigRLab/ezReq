# ezReq
Easy HttpClient Component for Python.

## Usage
```py
from ezreq import EzReq

e = EzReq("https://httpbin.org")
e.get("/get").text
e.post("post").text
```
