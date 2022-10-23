from typing import Callable
from framework.request import Request
from .base import BaseWsgiApplication


class Application(BaseWsgiApplication):

    def __call__(self, environ: dict, start_response: Callable) -> iter:
        request = Request(environ)
        start_response("200 ok", [("Content-Type", "text/html")])

        return [b"Hello World"]
