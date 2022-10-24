from typing import Callable, Iterable
from framework.request import Request
from framework.response import Response
from framework.types import StartResponseType


class BaseApplication:
    def validate_response(response: Response) -> None:
        pass

    def route(self, view_func: Callable[[Request], Response]) -> Callable:
        def application(environ: dict, start_response: StartResponseType) -> Iterable:
            request = Response(environ)
            response = view_func(request)
            if not isinstance(response, Response):
                raise TypeError(
                    f"You view should return and instance of the Response class not {type(response)}"
                )
            start_response(response.status, response.get_headers())
            return response
        return application
