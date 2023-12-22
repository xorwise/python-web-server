from typing import Callable, Literal, get_type_hints
import inspect
from server.exceptions import HTTPException

from server.request import HTTPRequest

ResponseModels = Literal["json", "html", "text", "file"]


class Configurator(object):
    _endpoints: dict[tuple[str, str], tuple[Callable, ResponseModels]] = {}
    _func_params: dict[Callable, tuple]

    @property
    def endpoints(self):
        return self._endpoints

    @endpoints.setter
    def endpoints(self, value) -> None:
        self._endpoints = value

    def _parse_path(self, func: Callable, path: str, query_params: dict):
        params = self._func_params[func]
        missing_params = []
        for param in params:
            if param["type_hint"] != HTTPRequest:
                if "{{{0}}}".format(param["name"]) not in path:
                    missing_params.append(param)

    def get_function_args(self, func: Callable):
        signature = inspect.signature(func)
        args = []
        type_hints = get_type_hints(func)

        for param_name in signature.parameters:
            arg_info = {
                "name": param_name,
                "type_hint": type_hints.get(param_name)
            }
            args.append(arg_info)
        self._func_params[func] = tuple(args)



    def get(self, path: str, response_model: ResponseModels) -> Callable:
        def get_decorator(func: Callable) -> None:
            self._endpoints[path, "GET"] = (func, response_model)
            self._func_params = self.get_function_args(func)

        return get_decorator

    def post(self, path: str, response_model: ResponseModels) -> Callable:
        def post_decorator(func: Callable) -> None:
            self._endpoints[path, "POST"] = (func, response_model)

        return post_decorator
