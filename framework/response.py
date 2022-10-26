from multiprocessing import context
import os
from typing import Any, Iterable, Iterator, Union, Optional
from http.client import responses
from jinja2 import Environment, FileSystemLoader


class ResponseBaseClass:
    _headers: dict
    _status_code: int
    _status_text: str

    def get_headers(self) -> Iterable[tuple[str, str]]:
        return list(self._headers.items())

    def set_headers(self, headers: Iterable[tuple[str, str]]) -> None:
        for key, value in headers:
            self._headers[key] = value

    def __call__(self, *_: Any, **__: Any) -> Iterator:
        return self

    @property
    def status(self) -> str:
        return f'{self._status_code} {self._status_text}'


class Response(ResponseBaseClass):
    def __init__(self, data: Union[str, bytes, tuple, list] = [], status_code: Optional[int] = 200, status_text: Optional[str] = None, headers: dict[str, str] = {}) -> None:
        self._data: list[bytes] = self._parse_data(data)
        self._status_code: int = status_code
        self._headers: dict[str, str] = headers
        self._status_text: str = status_text if status_text else responses.get(
            status_code, "")

    def __iter__(self):
        return iter(self._data)

    def _parse_data(self, data: Union[str, bytes, tuple, list]) -> None:
        """
        Parses the data entered by the user and returns an iterator that contains
        bytes data.
        """
        if not isinstance(data, (list, tuple, str, bytes)):
            raise ValueError(
                f"data must be either strin or bytestring or a iterable(tuple, list) of bytes not {type(data)}")
        if isinstance(data, bytes):
            return [data]
        if isinstance(data, str):
            return [data.encode('utf-8')]
        bytes_data = []
        for chunk in data:
            if not isinstance(chunk, (str, bytes)):
                raise ValueError(
                    f"Data can must be and iterable of str and bytes not {type(chunk)}"
                )
            if isinstance(chunk, str):
                bytes_data.append(chunk.encode("utf-8"))
                continue
            bytes_data.append(chunk)
        return bytes_data


class TemplateResponse(ResponseBaseClass):

    def __init__(self, name: str, status_code: Optional[int] = 200, status_text: Optional[str] = None,  context: Optional[dict[str, Any]] = {}, headers: dict[str, str] = {}) -> None:
        self.name = name
        self._status_code = str
        self._data: list = []
        self._context: dict[str, Any] = {}
        self._headers = headers
        self._status_text: str = status_text if status_text else responses.get(
            status_code, "")

    def __call__(self, app_path):
        """

        """
        template_dir = self._get_template_dir(app_path)
        self._data = self._load_template(template_dir)
        return self

    def _get_template_dir(self, application_path: str) -> str:
        parent = os.path.dirname(application_path)
        return os.path.join(parent, 'templates')

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def _load_template(self, template_dir: str) -> list:
        environ = Environment(loader=FileSystemLoader(template_dir))
        template = environ.get_template(self.name)
        return [template.render(**self._context).encode("utf-8")]
