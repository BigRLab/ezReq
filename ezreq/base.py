import re
from requests import Session

try:
  from urllib.parse import urljoin
except ImportError:
  from urlparse import urljoin

__all__ = ["EzReqError", "EzReq"]

# pylint: disable=line-too-long
_RE_FULL_URL = re.compile(r"^(?P<base_url>(?P<protocol>(?:ht|f)tps?\:)\/\/(?:[0-9A-Za-z][0-9A-Za-z_-]*\.)+(?:[A-Za-z]{2,}))(?:\/[0-9A-Za-z#%&./=?@_-]*)?$")

class EzReqError(Exception):
  pass


# pylint: disable=invalid-name
def normalize_url(fn):
  """
  @param fn: function
  A decorator of request method,
  which will normalize the url. like
  '/?page=rss' -> "http://example.org/?page=rss"
  """
  def wrapped_fn(self, url, **kwargs):
    matched = _RE_FULL_URL.match(url)

    if matched:
      self._base_url = matched.group("base_url")  # pylint: disable=W0212
      self._protocol = matched.group("protocol")  # pylint: disable=W0212

      if fn.__name__ == "__init__":
        self._last_url = url  # pylint: disable=W0212
        return fn(self, url, **kwargs)

    # Use getattr is safe for Class.__init__
    elif getattr(self, "_initiated", False): # pylint: disable=W0212
      if url.startswith(r"//"):
        # "//example.com"
        url = urljoin(self._protocol, url)   # pylint: disable=W0212
      elif url.startswith(r"?"):
        # "?page=rss"
        url = "/" + url  # -> "/?page=rss"
        url = urljoin(self._base_url, url)   # pylint: disable=W0212
      else:
        # "/?page=rss" "page=rss"
        url = urljoin(self._base_url, url)   # pylint: disable=W0212
    else:
      # Only happen in Class.__init__
      #
      # Reason(s):
      #   - Use "//example.com" in Class.__init__
      #   - Use "/?page=rss" in Class.__init__
      #   - Use Unsupported URI. Like "sftp://example.org"
      raise EzReqError("Unsupported URI!")

    # pylint: disable=W0212
    matched = _RE_FULL_URL.match(self._last_url)

    # pylint: disable=W0212
    self._session.headers.update({
      # HTTP/2 Headers lowercase only
      "origin": matched.group("base_url"),
      "referer": self._last_url
    })

    self._last_url = url  # pylint: disable=W0212
    return fn(self, url, **kwargs)

  return wrapped_fn


class EzReq(object):  # pylint: disable=R0205
  @normalize_url
  def __init__(self, base_url, **kwargs):
    self._base_url = base_url
    self._session = Session()
    self._last_url = base_url
    self._initiated = True

    headers = kwargs.get("headers", {})
    self._session.headers.update(headers)

  @normalize_url
  def get(self, url, **kwargs):
    return self._session.get(url, **kwargs)

  @normalize_url
  def post(self, url, **kwargs):
    return self._session.post(url, **kwargs)
