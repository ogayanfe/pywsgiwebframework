from typing import Any
from .stores import WsgiObjectsStore
import cgi


class Request:
    QUERY_STRING: str
    _WsgiObjectsStore = WsgiObjectsStore()

    def __init__(self, environ: dict[str, Any]) -> None:
        self.environ = environ
        self.HEADERS = {}
        for key, value in environ.items():
            if key.startswith("wsgi."):
                setattr(self._WsgiObjectsStore, key.replace(".", '_'), value)
                if key == "wsgi.url_scheme":
                    setattr(self, "url_scheme", value)
                continue

            if key.startswith("HTTP_"):
                self.HEADERS[key.replace("HTTP_", "")] = value
                continue

            setattr(self, key, value)

    def _parse_query_string(self, query_string: str) -> dict:
        """
        Converts a query string to a dictionary of its values
        for example, 
        name=ayanfe&lang=en should return {name: ayanfe, lang=en}
        """
        output = {}
        query_string_list = query_string.split("&")
        for item in query_string_list:
            key, value = item.split("=")
            output[key] = value
        return output

    @property
    def GET(self) -> dict:
        if self.QUERY_STRING == "":
            return {}
        return self._parse_query_string(self.QUERY_STRING)

    @property
    def POST(self) -> dict:
        fields = cgi.FieldStorage(
            fp=self._WsgiObjectsStore.wsgi_input, environ=self.environ, keep_blank_values=1)
        return dict(fields)
