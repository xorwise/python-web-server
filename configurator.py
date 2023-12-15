from typing import Callable, Literal
from response import HTTPResponse

ResponseModels = Literal["json", "html", "text", "file"]


class Configurator(object):
    _endpoints: dict[tuple[str, str], tuple[Callable, ResponseModels]] = {}

    @property
    def endpoints(self):
        return self._endpoints

    @endpoints.setter
    def endpoints(self, value):
        self._endpoints = value

    def get(self, path: str, response_model: ResponseModels):
        def get_decorator(func: Callable):
            self._endpoints[path, "GET"] = (func, response_model)

        return get_decorator
