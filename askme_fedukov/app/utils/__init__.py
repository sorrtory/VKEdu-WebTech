from django.urls import reverse_lazy
from urllib.parse import urlencode

def redirect_to(path='index', params=None, anchor="", **kwargs):
    """
    Returns a URL string for redirecting to the specified path with optional params and anchor.

    Example:
        redirect_to('question', params={'page': 2}, anchor='answer-10', id=5)
        -> '/question/5/?page=2#answer-10'
    """
    url = reverse_lazy(
        path, kwargs=kwargs) if kwargs else reverse_lazy(path)
    if params:
        if isinstance(params, dict):
            url += '?' + urlencode(params)
        elif isinstance(params, str):
            url += params if params.startswith('?') else '?' + params
    if anchor:
        url += f"#{anchor}"
    return url