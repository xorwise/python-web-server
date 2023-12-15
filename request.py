from exceptions import HTTPException
from urllib.parse import urlparse


class HTTPRequest(object):
    method: str = None
    uri: str = None
    http_version: str = None
    query_params: dict[str, str] = {}
    host: tuple[str, int] = None
    accept: dict[float, list[str]] = {}

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
            for query in parsed_url.query.split("&"):
                self.query_params.update({query.split("=")[0]: query.split("=")[1]})

        if len(words) > 2:
            self.http_version = words[2].decode()

        host_string = lines[1].split()[1].decode()
        self.host = (host_string.split(":")[0], int(host_string.split(":")[1]))
        for i in range(2, len(lines)):
            if "Accept:" in lines[i].decode():
                header = lines[i].split()[1].decode()
                parsed_values = self._parse_accept_header(header)

                for value, quality in parsed_values:
                    q_value = quality.get("q", 1.0)
                    if q_value in self.accept:
                        self.accept[q_value].append(value)
                    else:
                        self.accept[q_value] = [value]
                break

    def accept_types(self):
        types = []
        for key in self.accept:
            types += self.accept[key]
        return types
