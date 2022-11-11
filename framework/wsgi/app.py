from typing import Any, Callable
from framework.wsgi.base import BaseApplication


class Application(BaseApplication):
    def __call__(self, environ: dict[str, str], start_response: Callable[[str, Any], Callable]):
        url = environ['PATH_INFO']
        method = environ["REQUEST_METHOD"]
        setattr(self, "environ", environ)
        view = self._get_route(url, method)
        response = view(environ, start_response)
        return response
