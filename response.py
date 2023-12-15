import json

CONTENT_TYPES = {
    "json": "application/json",
    "html": "text/html",
    "text": "text/plain",
    "file": "application/octet-stream",
}


class HTTPResponse(object):
    status_code: int
    response_model: str
    data: object
    headers = {
        "Server": "SimpleHTTP",
        "Content-Type": "text/html",
    }

    status_codes = {
        200: "OK",
        404: "Not Found",
        500: "Internal error",
        501: "Not Implemented",
    }
    response_line: str

    def __init__(self, status_code, response_model, data):
        self.status_code = status_code
        self.response_model = response_model
        self.data = data

    def _response_line(self, status_code: int):
        reason = self.status_codes.get(status_code)
        return f"HTTP/1.1 {status_code} {reason}\r\n".encode()

    def _response_headers(self, extra_headers=None):
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)

            new_headers = []
            for key, value in headers.items():
                new_headers.append(f"{key}: {value}\r\n".encode())
        else:
            return headers

        return b"".join(new_headers)

    def _parse_data(self, data):
        match self.response_model:
            case "json":
                return json.dumps(data).encode()
            case "html":
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

    def __call__(self):
        try:
            parsed_data = self._parse_data(self.data)
        except Exception:
            response_line = self._response_line(500)
            headers = self._response_headers()
            return b"".join(
                [response_line, headers, b"\r\n", b"<h1>Internal error</h1>"]
            )
        response_line = self._response_line(200)
        headers = self._response_headers(
            extra_headers={"Content-Type": CONTENT_TYPES[self.response_model]}
        )
        print(headers)
        return b"".join(
            [
                response_line,
                headers,
                b"\r\n",
                parsed_data,
            ]
        )
