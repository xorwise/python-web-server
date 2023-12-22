import json
from urllib.parse import urlparse, parse_qs
from typing import Any, Literal


class HTTPRequest(object):
    method: str = None
    uri: str = None
    http_version: str = None
    query_params: dict[str, list[str]] = {}
    host: tuple[str, int] = None
    accept: dict[float, list[str]] = {}
    content_type: Literal["text/plain", "text/html", "application/json"] = "application/json"
    cookies: dict[str, str] = {}
    body: str = ""
    data: Any = None

    @staticmethod
    def _parse_accept_header(accept_header):
        accept_values = accept_header.split(",")

        result = []

        for val in accept_values:
            mime_type, *params = val.strip().split(";")
            media_range = mime_type.strip()

            quality = 1.0

            for param in params:
                param_name, param_value = param.split("=")
                param_name = param_name.strip()

                if param_name == "q":
                    quality = float(param_value.strip())

            result.append((media_range, {"q": quality}))

        result.sort(key=lambda x: x[1]["q"], reverse=True)

        return result

    def parse(self, data):
        lines = data.split(b"\r\n")

        request_line = lines[0]
        words = request_line.split(b" ")
        self.method = words[0].decode()

        if len(words) > 1:
            url = words[1].decode()
            parsed_url = urlparse(url)
            self.uri = parsed_url.path
            self.query_params = parse_qs(parsed_url.query)

        if len(words) > 2:
            self.http_version = words[2].decode()

        host_string = lines[1].split()[1].decode()
        self.host = tuple(host_string.split(":"))

        for line in lines[2:]:
            line = line.decode()
            if line.startswith("Accept:"):
                header = line.split(":")[1].strip()
                parsed_values = self._parse_accept_header(header)

                for value, quality in parsed_values:
                    q_value = quality.get("q", 1.0)
                    if q_value in self.accept:
                        self.accept[q_value].append(value)
                    else:
                        self.accept[q_value] = [value]
            elif line.startswith("Cookie:"):
                header = line.split(":")[1].strip()
                for cookie in header.split(";"):
                    try:
                        name, value = cookie.split("=")
                        self.cookies[name.strip()] = value.strip()
                    except ValueError:
                        continue
            elif line.startswith("Content-Type:"):
                self.content_type = line.split(":")[1].strip()

        self.body = lines[-1].decode()
        self.parse_body()

    def parse_body(self):
        if not self.body:
            return
        match self.content_type:
            case "text/plain":
                self.data = str(self.body)
            case "text/html":
                self.data = str(self.body)
            case "application/json":
                self.data = json.loads(self.body)

    def set_cookies(self, cookies: dict[str, str | Any]):
        for key, value in cookies.items():
            self.cookies[key] = str(value)
        self.cookies.update(cookies)

    def accept_types(self):
        types = []
        for key in self.accept:
            types += self.accept[key]
        return types
