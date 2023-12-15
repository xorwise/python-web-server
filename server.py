import socket
import json
import os
from configurator import Configurator
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
        request = HTTPRequest()
        request.parse(data)

        try:
            handler = getattr(self, "handle_" + request.method)
        except AttributeError:
            handler = self.HTTP_501_handler

        response = handler(request)

        return response

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
        if not func and not response_model:
            return self.HTTP_404_handler(request)
        try:
            data = func(request)
        except Exception:
            return self.HTTP_500_handler(request)

        response = HTTPResponse(200, response_model, data)
        return response()
