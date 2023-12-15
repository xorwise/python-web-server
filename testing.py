from configurator import Configurator
from request import HTTPRequest
from server import HTTPServer

configurator = Configurator()


@configurator.get("/", response_model="json")
def get_index(request: HTTPRequest) -> list[dict]:
    users = [
        {"name": "John", "age": 30},
        {"name": "Jane", "age": 25},
        {"name": "Bob", "age": 40},
        {"name": "Alice", "age": 35},
    ]
    return users


if __name__ == "__main__":
    server = HTTPServer(configurator)
    print(configurator.endpoints)
    server.start()
