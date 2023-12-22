from server.web import Server
from server.configurator import Configurator
import asyncio

def run(configurator: Configurator, host: str = "127.0.0.1", port: int = 8888, ws_port: int = 8887):
    server = Server(configurator, host, port)
    asyncio.run(server.start())

    


