from typing import Callable, Iterable, Union
from framework.defaults import default_404_view
from framework.request import Request
from framework.response import Response, ResponseBaseClass
from framework.common_types import StartResponseType
from framework.utils import convert_url_to_regex
import re


class BaseApplication:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._url_to_view: dict[str, Callable] = {}
        self._page_not_found_view = self._make_application(default_404_view)

    def _validate_response(response: Response) -> None:
        pass

    def _make_application(self, view_func: Callable[[Request], Response], **kwargs):
        """
        Takes a view function and returns a WSGI application, should not be called directly
        """

        def application(environ: dict, start_response: StartResponseType) -> Iterable:
            request = Request(environ)
            response = view_func(request, **kwargs)
            if not isinstance(response, ResponseBaseClass):
                raise TypeError(
                    f"You view should return and instance of the Response class not {type(response)}"
                )
            start_response(response.status, response.get_headers())
            return response(self._file_path)
        return application

    def route(self, url: str):
        """
        Defines which route to be called when a user navigates to a particular url
        """
        def decorator(view_func: Callable[[Request], Response]) -> Callable:
            self.map_route(url, view_func)
            return view_func
        return decorator

    def route_404(self):
        """
        Just like the route view, defines the view to be called when a 404 error occurs

        @app.route_404()
        def page_404(request):
            return Response("<h1>Page Not Found</h1>", status_code=404, headers={})

        If a user goes to a non existent page page_404 will be called. 
        """

        def decorator(view_func: Callable[[Request], Response]) -> Callable:
            self._page_not_found_view = view_func
            return view_func
        return decorator

    def map_route(self, url: str, view: Callable):
        self._url_to_view[convert_url_to_regex(url)] = view

    def _process_match(self, matches: dict[str, str]) -> dict[str, Union[str, int, float]]:
        """
        Converts the matches found by the regexp to the corresponding types
        denoted by the regexp
        """
        output: dict[str, Union[str, int, float]] = {}
        for key, value in matches.items():
            if key.startswith("int_"):
                output[key.replace("int_", "")] = int(value)
                continue
            if key.startswith("str_"):
                output[key.replace("str_", "")] = str(value)
                continue
            if key.startswith("float_"):
                output[key.replace("float_", "")] = float(value)
                continue
        return output

    def _get_route(self, url: str) -> Callable[[dict[str, str], StartResponseType], Callable]:
        for key, view in self._url_to_view.items():
            match = re.match(key, url)
            if match:
                kwargs = self._process_match(match.groupdict())
                return self._make_application(view, **kwargs)
        return self._page_not_found_view
