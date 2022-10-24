from typing import Iterable, Union, Optional
from http.client import responses


class Response:
    def __init__(self, data: Union[str, bytes, tuple, list], status_code: int, status_text: Optional[str] = None, headers: dict[str, str] = {}) -> None:
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

    def get_headers(self) -> Iterable[tuple[str, str]]:
        return list(self._headers.items())

    def set_headers(self, headers: Iterable[tuple[str, str]]) -> None:
        for key, value in headers:
            self._headers[key] = value

    @property
    def status(self) -> str:
        return f'{self._status_code} {self._status_text}'
