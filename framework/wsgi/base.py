from typing import Callable, Iterable, List, Tuple, Union, Optional
from framework.defaults import default_404_view
from framework.request import Request
from framework.response import BaseResponse, StaticResponse
from framework.common_types import StartResponseType
from framework.utils import check_http_methods, convert_url_to_regex, get_directory_file_paths
import re
import os


class BaseApplication:
    environ: dict[str, str]

    def __init__(self, file_path: str) -> None:
        self._project_directory = os.path.dirname(file_path)
        self._url_to_view: dict[str, List[Tuple(str, Callable)]] = {
            "global": []  # Views that respond to all http methods
        }
        self._page_not_found_view = default_404_view
        self._static_dir_files: list[str] = get_directory_file_paths(
            os.path.join(self._project_directory, "static")
        )

    def _validate_response(response: BaseResponse) -> None:
        pass

    def _make_application(self, view_func: Callable[[Request], BaseResponse], **kwargs,):
        """
        Takes a view function and returns a WSGI application, should not be called directly
        """

        def application(environ: dict, start_response: StartResponseType) -> Iterable:
            request = Request(environ)
            response = view_func(request, **kwargs)
            if not isinstance(response, BaseResponse):
                raise TypeError(
                    f"You view should return and instance of the Response class not {type(response)}"
                )
            start_response(response.status, response.get_headers())
            return response(self._project_directory, environ)
        return application

    def route_404(self):
        """
        Just like the route view, defines the view to be called when a 404 error occurs

        @app.route_404()
        def page_404(request):
            return Response("<h1>Page Not Found</h1>", status_code=404, headers={})

        If a user goes to a non existent page page_404 will be called.
        """

        def decorator(view_func: Callable[[Request], BaseResponse]) -> Callable:
            self._page_not_found_view = view_func
            return view_func
        return decorator

    def route(self, url: str, methods: Optional[List[str]] = None):
        """
        Defines which route to be called when a user navigates to a particular url
        """
        if methods is None:
            methods = ["get", "post", "put", "patch", "delete"]
        check_http_methods(methods)

        def decorator(view_func: Callable[[Request], BaseResponse]) -> Callable:
            self._map_route(url, view_func, methods)
            return view_func
        return decorator

    def _map_route(self, url: str, view: Callable, methods: List[str]) -> None:
        """
        Maps a url pattern to a wsgi to a view
        """
        url_regex = convert_url_to_regex(url)
        if len(methods) == 5:  # responds to all http methods
            self._url_to_view["global"].append((url_regex, view))
            return
        for method in methods:
            _method = method.lower()
            if self._url_to_view.get(_method, None) is None:
                self._url_to_view[_method] = []
            self._url_to_view[_method].append((url_regex, view))

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

    def _get_static_route(self, url: str) -> Union[None, Callable]:
        """
        Checks the static files for a match in the url and returns an application
        returns None otherwise
        """
        for file_path in self._static_dir_files:  # Check static files
            stripped_path = file_path.replace(self._project_directory, "")
            bash_path = stripped_path.replace("\\", '/')  # For Windows Devices

            if bash_path == url:
                def _(*__, **___):
                    return StaticResponse(file_path)
                return self._make_application(_)
        return None

    def _get_application_from_url_method(self, url: str, method: str):
        """
        Checks the method and returns the application involved with the 
        url else returns None
        """
        method_views = self._url_to_view.get(method, None)
        if not method_views:
            return
        for key, view in method_views:
            match = re.match(key, url)
            if match:
                kwargs = self._process_match(match.groupdict())
                return self._make_application(view, **kwargs)

    def _get_route(self, url: str, method: str) -> Callable[[dict[str, str], StartResponseType], Callable]:
        """
        Takes in the a resource url and return the application to be called, if any.
        First checks the user defined routes, then check the files in the static directory else
        routes the request to the 404 view
        """

        global_application = self._get_application_from_url_method(
            url, "global"
        )
        if global_application:
            return global_application
        method_application = self._get_application_from_url_method(
            url, method.lower()
        )
        if method_application:
            return method_application

        static_application = self._get_static_route(url)
        if static_application:
            return static_application
        return self._make_application(self._page_not_found_view)
