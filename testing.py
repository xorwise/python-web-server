from configurator import Configurator
from exceptions import HTTPException
from request import HTTPRequest
from server import HTTPServer

configurator = Configurator()
users = [
    {"name": "John", "age": 30},
    {"name": "Jane", "age": 25},
    {"name": "Bob", "age": 40},
    {"name": "Alice", "age": 35},
]


@configurator.get("/", response_model="json")
def get_home(request: HTTPRequest) -> list[dict]:
    return users


@configurator.get("/index", response_model="html")
def get_index(request: HTTPRequest) -> str:
    filename = "src/index.html"
    return filename


@configurator.get("/user", response_model="json")
def get_user(request: HTTPRequest) -> dict:
    user = None
    for u in users:
        if u["name"] == request.query_params.get("name"):
            user = u
    if not user:
        raise HTTPException(404, detail="User not found")
    return user


if __name__ == "__main__":
    server = HTTPServer(configurator)
    print(configurator.endpoints)
    server.start()
