import socket
from configurator import Configurator
from exceptions import HTTPException
from response import HTTPResponse
from request import HTTPRequest


class TCPServer:
    def __init__(self, configurator: Configurator, host="127.0.0.1", port="8888"):
        self.configurator = configurator
        self.host = host
        self.port = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((self.host, int(self.port)))

        s.listen(5)

        print("Listening at", s.getsockname())

        while True:
            conn, addr = s.accept()

            print("Connected by ", addr)

            data = conn.recv(1024)
            response = self.handle_request(data)

            conn.sendall(response)

            conn.close()

    def handle_request(self, data):
        return data


class HTTPServer(TCPServer):
    def handle_request(self, data):
        try:
            request = HTTPRequest()
            request.parse(data)

            try:
                handler = getattr(self, "handle_" + request.method)
                response = handler(request)
            except AttributeError:
                handler = self.HTTP_501_handler
            return response
        except Exception as e:
            if isinstance(e, HTTPException):
                if request.uri is not None:
                    response = HTTPResponse(
                        e.status_code,
                        self.configurator.endpoints.get(request.uri)[1],
                        e.detail,
                    )
                else:
                    response = HTTPResponse(
                        e.status_code, "html", f"<h1>{e.detail}</h1>"
                    )
            else:
                response = HTTPResponse(500, "json", data="Internal server error")
            return response()

    def HTTP_404_handler(self, request: HTTPRequest):
        data = "<h1>Not found</h1>"
        response = HTTPResponse(404, "html", data)
        return response()

    def HTTP_500_handler(self, request: HTTPRequest):
        data = "<h1>Internal server error</h1>"
        response = HTTPResponse(500, "html", data)
        return response()

    def HTTP_501_handler(self, request: HTTPRequest):
        data = "<h1>Not implemented</h1>"
        response = HTTPResponse(501, "html", data)
        return response()

    def handle_GET(self, request: HTTPRequest):
        func, response_model = self.configurator.endpoints.get(
            (request.uri, "GET"), (None, None)
        )
        if (not func and not response_model) or (
            response_model not in request.accept_types()
        ):
            return self.HTTP_404_handler(request)
        try:
            data = func(request)
        except HTTPException as e:
            response = HTTPResponse(
                e.status_code,
                self.configurator.endpoints.get((request.uri, "GET"))[1],
                e.detail,
            )
            return response()

        if isinstance(data, HTTPResponse):
            return data()
        response = HTTPResponse(200, response_model, data)
        return response()
