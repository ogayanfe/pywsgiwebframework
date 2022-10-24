from typing import Any, Callable
from framework.wsgi.base import BaseApplication


class Application(BaseApplication):
    def __call__(self, environ: dict[str, str], start_response: Callable[[str, Any], Callable]):
        status = "200 ok"
        headers = [("content-type", "text/html")]
        start_response(status, headers)

        return [b'<h1>It Works</h1>']
