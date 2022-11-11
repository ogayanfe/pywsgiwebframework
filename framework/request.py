from typing import Any, BinaryIO
from urllib.parse import unquote
import cgi


class WsgiStore:
    wsgi_input: BinaryIO
    wsgi_error: BinaryIO
    environ: dict[str, str]

    def get_input(self):
        x = cgi.FieldStorage(fp=self.wsgi_input, environ=self.environ)
        return dict(x)


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
            if key == 'REQUEST_METHOD':
                setattr(self, 'METHOD', value)
            else:
                setattr(self, key, value)
        setattr(self._wsgi_store, 'environ', environ)

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

    @property
    def POST(self):
        return self._wsgi_store.get_input()
