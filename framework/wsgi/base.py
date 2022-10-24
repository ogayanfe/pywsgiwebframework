from typing import Callable, Iterable
from framework.request import Request
from framework.response import Response
from framework.types import StartResponseType


class BaseApplication:
    def __init__(self):
        self._url_to_view: dict[str, Callable] = {}
        self._page_not_found_view = None

    def _validate_response(response: Response) -> None:
        pass

    def map_404_view(self, view: Callable):
        self._page_not_found_view = view

    def view(self, view_func: Callable[[Request], Response]) -> Callable:
        def application(environ: dict, start_response: StartResponseType) -> Iterable:
            request = Request(environ)
            response = view_func(request)
            if not isinstance(response, Response):
                raise TypeError(
                    f"You view should return and instance of the Response class not {type(response)}"
                )
            start_response(response.status, response.get_headers())
            return response
        return application

    def map_route(self, url: str, view: Callable):
        self._url_to_view[url] = view

    def _get_route(self, url: str) -> Callable[[dict[str, str], StartResponseType], Callable]:
        return self._url_to_view.get(url, self._page_not_found_view)
