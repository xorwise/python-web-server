from typing import Callable, Literal, get_type_hints
import inspect
from server.exceptions import EnpointParseException
import re

ResponseModels = Literal["json", "html", "text", "file"]


class Configurator(object):
    _endpoints: dict[tuple[str, str], tuple[Callable, ResponseModels]] = {}
    _func_params: dict[Callable, dict] = {}

    @property
    def endpoints(self):
        return self._endpoints

    @endpoints.setter
    def endpoints(self, value) -> None:
        self._endpoints = value

    @property
    def func_params(self):
        return self._func_params

    @staticmethod
    def _path_to_regex(path: str) -> str:
        regex_pattern = re.sub(r"{(.*?)}", r"(?P<\1>[^\/]+)", path)
        return f"^{regex_pattern}$"

    @staticmethod
    def _extract_parameters(path: str, regex_pattern: str) -> dict:
        match = re.match(regex_pattern, path)
        if match:
            return match.groupdict()
        return {}

    def get_function_args(self, func: Callable):
        signature = inspect.signature(func)
        args = {}
        type_hints = get_type_hints(func)

        for param_name in signature.parameters:
            args[param_name] = type_hints.get(param_name)
        self.func_params[func] = args

    def get(self, path: str, response_model: ResponseModels) -> Callable:

        def get_decorator(func: Callable) -> None:
            path_regex = self._path_to_regex(path)
            parameters = self._extract_parameters(path, path_regex)
            self._endpoints[path_regex, "GET"] = (func, response_model)
            self.get_function_args(func)
            for param in parameters:
                if param not in self._func_params[func]:
                    raise EnpointParseException(f"Missing parameter: {param}")

        return get_decorator

    def post(self, path: str, response_model: ResponseModels) -> Callable:

        def post_decorator(func: Callable) -> None:
            path_regex = self._path_to_regex(path)
            parameters = self._extract_parameters(path, path_regex)
            self._endpoints[path_regex, "POST"] = (func, response_model)
            self.get_function_args(func)
            for param in parameters:
                if param not in self._func_params[func]:
                    raise EnpointParseException(f"Missing parameter: {param}")

        return post_decorator
