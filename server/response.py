import json
from http import HTTPStatus
import os
from typing import Any


CONTENT_TYPES = {
    "json": "application/json",
    "html": "text/html",
    "text": "text/plain",
    "file": "application/octet-stream",
}


class HTTPResponse(object):
    status_code: int = 200
    response_model: str = "json"
    data: object
    headers = {
        "Server": "SimpleHTTP",
        "Content-Type": "text/html",
    }

    status_codes = {int(v): v.phrase for v in HTTPStatus.__members__.values()}
    response_line: str

    def __init__(self, status_code: int, response_model: str = "html", data: Any = b""):
        self.status_code = status_code
        self.response_model = response_model
        self.data = data

    async def _response_line(self, status_code: int):
        reason = self.status_codes.get(status_code)
        return f"HTTP/1.1 {status_code} {reason}\r\n".encode()

    async def _response_headers(self, extra_headers=None):
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)

            new_headers = []
            for key, value in headers.items():
                new_headers.append(f"{key}: {value}\r\n".encode())
        else:
            return headers

        return b"".join(new_headers)

    async def _parse_data(self, data):
        match self.response_model:
            case "json":
                return json.dumps(data).encode()
            case "html":
                if os.path.exists(str(data)):
                    with open(str(data), "rb") as f:
                        return f.read()
                return str(data).encode()
            case "text":
                return str(data).encode()
            case "file":
                with open(f"src/{data}", "rb") as f:
                    new_data = f.read()
                return new_data
            case _:
                if isinstance(data, bytes):
                    return data
                else:
                    return f"{data}".encode()

    async def __call__(self):
        try:
            if self.data:
                parsed_data = await self._parse_data(self.data)
            else:
                parsed_data = self.status_codes[self.status_code]
        except Exception:
            response_line = await self._response_line(500)
            headers = await self._response_headers()
            return b"".join(
                [response_line, headers, b"\r\n", b"<h1>Internal error</h1>"]
            )
        response_line = await self._response_line(self.status_code)
        headers = await self._response_headers(
            extra_headers={"Content-Type": CONTENT_TYPES[self.response_model], "Content-Length": len(parsed_data)}
        )
        return b"".join(
            [
                response_line,
                headers,
                b"\r\n",
                parsed_data,
            ]
        )
