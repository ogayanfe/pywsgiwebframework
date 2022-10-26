import os
from typing import Any, Iterable, Iterator, Union, Optional, IO
from http.client import responses
from jinja2 import Environment, FileSystemLoader
import mimetypes


class BaseResponse:
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


class Response(BaseResponse):
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


class TemplateResponse(BaseResponse):

    def __init__(self, name: str, status_code: Optional[int] = 200, status_text: Optional[str] = None,  context: Optional[dict[str, Any]] = {}, headers: dict[str, str] = {}) -> None:
        self.name = name
        self._status_code: int = status_code
        self._data: list = []
        self._context: dict[str, Any] = {}
        self._headers = headers
        self._status_text: str = status_text if status_text else responses.get(
            status_code, ""
        )

    def __call__(self, project_path, *_, **kwargs):
        """
        Read the templates and return an iterable response body, 
        in this case myself
        """
        template_dir: str = os.path.join(project_path, "templates")
        self._data: list[bytes] = self._load_template(template_dir)
        return self

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def _load_template(self, template_dir: str) -> list:
        environ = Environment(loader=FileSystemLoader(template_dir))
        template = environ.get_template(self.name)
        return [template.render(**self._context).encode("utf-8")]


class StaticResponse(BaseResponse):

    def __init__(self, file_path: str, status_code: int = 200, status_text: Optional[str] = None, headers: dict[str, str] = {}):
        self._file_path: str = file_path
        self._status_code: int = status_code
        self._status_text: str = status_text if status_text else responses.get(
            status_code, "")
        self._headers: dict[str, str] = headers
        self.file_object: IO = open(file_path, 'rb')

    def close(self):
        self.file_object.close()

    def __iter__(self):
        return self.file_wrapper(self.file_object)

    def __call__(self, _, environ: dict[str, str]) -> Iterator:
        setattr(self, "file_wrapper", environ.get("wsgi.file_wrapper"))
        return self

    def get_headers(self) -> Iterable[tuple[str, str]]:
        mtype, encoding = mimetypes.guess_type(self._file_path)
        output = {
            "content-type": mtype,
            "content-encoding": encoding if encoding else "",
        }
        for key, value in self._headers.items():
            output[key.lower()] = value
        return output.items()
