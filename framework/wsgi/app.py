from typing import Any, Callable
from framework.wsgi.base import BaseApplication


class Application(BaseApplication):
    def __call__(self, environ: dict[str, str], start_response: Callable[[str, Any], Callable]):
        url = environ['PATH_INFO']
        view = self._get_route(url)
        response = view(environ, start_response)
        return response
