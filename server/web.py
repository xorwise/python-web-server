import asyncio
import traceback
from server.request import HTTPRequest
from server.exceptions import HTTPException
from server.response import HTTPResponse, CONTENT_TYPES
from typing import Callable, Literal
from server.configurator import Configurator
import re


class TCPServer:

    def __init__(self,
                 configurator: Configurator,
                 host="127.0.0.1",
                 port="8888"):
        self.configurator: Configurator = configurator
        self.host: str = host
        self.port: int = port

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host,
                                            int(self.port))

        async with server:
            print("Server started. Listening at",
                  server.sockets[0].getsockname())
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        try:
            addr = ":".join(
                [str(i) for i in writer.get_extra_info("peername")])
            print("New connection from " + addr)
            while True:
                data = await reader.read(1024)
                print("Received data from " + addr)
                if not data:
                    break

                response = await self.handle_request(data)
                writer.write(response)
                await writer.drain()
                print("Response has been sent to " + addr)

        except Exception as e:
            print(traceback.format_exc())
        finally:
            writer.close()
            print(f"Connection with {addr} closed")

    async def handle_request(self, data):
        return data


class Server(TCPServer):

    async def handle_request(self, data):
        try:
            request = HTTPRequest()
            request.parse(data)

            try:
                handler = getattr(self, f"handle_{request.method}",
                                  self.handle_not_implemented)
                response = await handler(request)
            except HTTPException as e:
                response = await self.handle_exception(request, e)

            return response

        except Exception as e:
            print(traceback.format_exc())
            response = HTTPResponse(500, "json", data="Internal server error")
            return await response()

    async def handle_exception(self, request, e):
        if request.uri is not None:
            response_model = self.configurator.endpoints.get(
                request.uri, ("html", f"<h1>{e.detail}</h1>"))[1]
            response = HTTPResponse(e.status_code, response_model, e.detail)
        else:
            response = HTTPResponse(e.status_code, "html",
                                    f"<h1>{e.detail}</h1>")
        return await response()

    async def handle_not_implemented(self, request):
        return HTTPResponse(501, data="<h1>Not implemented</h1>")

    async def handle_GET(self, request):
        parameters, func, response_model, code = self.is_uri_exists(request)
        match code:
            case 0:
                response = HTTPResponse(405,
                                        data="<h1>Method not allowed</h1>")
                return await response()
            case -1:
                response = HTTPResponse(404, data="<h1>Not found</h1>")
                return await response()
            case 1:
                response = HTTPResponse(406, data="<h1>Not acceptable</h1>")
                return await response()

        try:
            converted_parameters = self.convert_parameters(
                request, parameters, func)
            print(converted_parameters)
            data = await func(**converted_parameters)
        except HTTPException as e:
            detail = e.detail
            response = HTTPResponse(e.status_code, response_model, detail)
            return await response()

        if isinstance(data, HTTPResponse):
            return data()

        response = HTTPResponse(200, response_model, data)
        return await response()

    async def handle_POST(self, request):
        parameters, func, response_model, code = self.is_uri_exists(request)

        match code:
            case 0:
                response = HTTPResponse(405,
                                        data="<h1>Method not allowed</h1>")
                return await response()
            case -1:
                response = HTTPResponse(404, data="<h1>Not found</h1>")
                return await response()
            case 1:
                response = HTTPResponse(406, data="<h1>Not acceptable</h1>")
                return await response()

        try:
            converted_parameters = self.convert_parameters(
                request, parameters, func)
            #TODO: add *args, **kwargs support
            data = await func(**converted_parameters)
        except HTTPException as e:
            detail = e.detail
            response = HTTPResponse(e.status_code, response_model, detail)
            return await response()

        if isinstance(data, HTTPResponse):
            return data()

        response = HTTPResponse(200, response_model, data)
        return await response()

    def is_uri_exists(
        self, request: HTTPRequest
    ) -> tuple[dict, Callable, str, int] | tuple[None, None, None, int]:
        found_match = False
        for key, value in self.configurator.endpoints.items():
            match = re.match(key[0], request.uri)
            if match and key[1] == request.method:
                found_match = True
                if CONTENT_TYPES.get(value[1]) not in request.accept_types():
                    return None, None, None, 1
                return match.groupdict(), value[0], value[1], 2
        if found_match:
            return None, None, None, 0

        return None, None, None, -1

    def convert_parameters(self, request: HTTPRequest, parameters: dict,
                           func: Callable):
        converted_parameters = {}
        for key, value in parameters.items():
            try:
                converted_parameters[key] = self.configurator.func_params[
                    func][key](value)
            except Exception:
                raise HTTPException(
                    422, "Validation error, can't conver parameter: " + key)
        for key, value in self.configurator.func_params[func].items():
            if value == HTTPRequest:
                converted_parameters[key] = request
        return converted_parameters
