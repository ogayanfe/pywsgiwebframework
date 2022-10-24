from typing import IO, Any, Iterable, Union
from urllib.parse import unquote


class WsgiStore:
    wsgi_input: IO
    wsgi_error: IO


class Request:
    wsgi_store = WsgiStore()
    REQUEST_URL: str
    QUERY_STRING: str

    def __init__(self, environ: dict[str, Any]):
        for key, value in environ.items():
            if not key.startswith("HTTP_"):
                setattr(self, key.replace("HTTP_", ""), value)
                continue

            if key.startswith("wsgi."):
                setattr(self.wsgi_store, key.replace("wsgi.", "wsgi_"), value)
                continue

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
    def GET(self) -> dict[str, Union[str, Iterable]]:
        query_string = self.QUERY_STRING
        return self._parse_query_string(query_string)
