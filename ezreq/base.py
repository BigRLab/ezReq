# Copyright (C) 2019 urain39 <urain39@qq.com>

from yurl import URL
from functools import wraps
from requests import Session
from requests.adapters import HTTPAdapter

try:
  from urllib.parse import urljoin
except ImportError:
  from urlparse import urljoin

try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode


__all__ = ['EzReqError', 'EzReqURLError', 'EzReq']


class EzReqError(Exception):
  pass

class EzReqURLError(EzReqError):
  pass


# pylint: disable=invalid-name
def normalize_url(fn):
  '''
  @param fn: function
  A decorator of request method,
  which will normalize the url. like
  '/?page=rss' -> 'http://example.com/?page=rss'
  '''
  @wraps(fn)
  def wrapped_fn(self, url, **kwargs):
    u = URL(url)

    # Fix params not appears in referer
    try:
      params = kwargs.pop('params')
      url = '{url}?{params}'.format(url=url, params=urlencode(params))
    except KeyError:
      pass

    if u.scheme and u.host:
      self._base_url = str(u.replace(full_path=''))
      self._scheme = u.scheme  # Update scheme

    if url.startswith(r'//'):
      # '//example.com'
      url = '{scheme}:{where}'.format(scheme=self._scheme, where=url)
      self._base_url = url                 # pylint: disable=protected-access
    elif url.startswith(r'?'):
      # '?page=rss'
      url = '/' + url  # -> '/?page=rss'
      url = urljoin(self._base_url, url)   # pylint: disable=protected-access
    else:
      # '/?page=rss' 'page=rss'
      url = urljoin(self._base_url, url)   # pylint: disable=protected-access

    # pylint: disable=protected-access
    u = URL(self._last_url)

    # pylint: disable=protected-access
    self._headers.update({
      # HTTP/2 Headers lowercase only
      'origin': str(u.replace(full_path='')),
      'referer': self._last_url
    })

    self._last_url = url  # pylint: disable=protected-access
    return fn(self, url, **kwargs)

  return wrapped_fn


class EzReq(object):  # pylint: disable=useless-object-inheritance
  def __init__(self, base_url, **kwargs):
    u = URL(base_url)

    if not (u.scheme and u.host):
      raise EzReqURLError('Unsupported URL!')

    # Backup scheme
    self._scheme = u.scheme

    self._base_url = base_url
    self._session = Session()
    self._last_url = base_url

    # `self._headers` -> `self._session.headers`
    self._headers = self._session.headers

    headers = kwargs.pop('headers', {})
    self._session.headers.update(headers)

    max_retries = kwargs.pop('max_retries', 3)
    self._session.mount('http://', HTTPAdapter(max_retries=max_retries))
    self._session.mount('https://', HTTPAdapter(max_retries=max_retries))

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    pass

  @normalize_url
  def get(self, url, **kwargs):
    self._headers.pop('origin')
    return self._session.get(url, **kwargs)

  @normalize_url
  def post(self, url, **kwargs):
    self._headers.pop('referer')
    return self._session.post(url, **kwargs)

  @normalize_url
  def visit(self, url, **kwargs):
    '''
    visit a url without `referer` and `origin`.
    '''
    self._headers.pop('origin')
    self._headers.pop('referer')
    return self._session.get(url, **kwargs)

  @property
  def session(self):
    return self._session
