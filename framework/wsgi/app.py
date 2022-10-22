from typing import Callable


class BaseWsgiApplication:
    def __call__(self, environ:dict, start_response: Callable) -> iter:
        pass


class Application(BaseWsgiApplication):
    pass