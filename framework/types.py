from typing import Type, Callable, Iterable

StartResponseType = Type[Callable[[str, Iterable[tuple[str, str]]], Callable]]
