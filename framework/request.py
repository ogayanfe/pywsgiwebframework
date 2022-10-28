from typing import Any, BinaryIO
from urllib.parse import unquote


class WsgiStore:
    wsgi_input: BinaryIO
    wsgi_error: BinaryIO


class Request:
    _wsgi_store = WsgiStore()
    REQUEST_URL: str
    QUERY_STRING: str

    def __init__(self, environ: dict[str, Any]):
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                setattr(self, key.replace("HTTP_", ""), value)
            elif key.startswith("wsgi."):
                setattr(self._wsgi_store, key.replace("wsgi.", "wsgi_"), value)
            else:
                setattr(self, key, value)

    def _parse_query_string(self, qs: str) -> dict[str, str]:
        if qs == "":
            return {}
        output = {}
        query_list = qs.split("&")
        for value in query_list:
            key, value = value.split("=")
            output[unquote(key)] = unquote(value)
        return output

    @property
    def GET(self) -> dict[str, str]:
        """
        Returns a dictionary of key, value pairs of the request url query parameters,
        """
        query_string = self.QUERY_STRING
        return self._parse_query_string(query_string)
