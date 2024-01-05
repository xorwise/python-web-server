from server.configurator import Configurator
from server.exceptions import HTTPException
from server.request import HTTPRequest
import server

configurator = Configurator()
users = [
    {
        "name": "John",
        "age": 30
    },
    {
        "name": "Jane",
        "age": 25
    },
    {
        "name": "Bob",
        "age": 40
    },
    {
        "name": "Alice",
        "age": 35
    },
]


@configurator.get("/", response_model="json")
async def get_home(request: HTTPRequest) -> list[dict]:
    return users


@configurator.get("/index", response_model="html")
async def get_index(request: HTTPRequest) -> str:
    filename = "src/index.html"
    return filename


@configurator.get("/user", response_model="json")
async def get_user(request: HTTPRequest) -> dict:
    user = None
    for u in users:
        if u["name"] == request.query_params.get("name", ["tt"])[0]:
            user = u
    if not user:
        raise HTTPException(404, detail="User not found")
    return user


@configurator.post("/user", response_model="json")
async def post_user(request: HTTPRequest) -> str:
    new_user = request.data
    return new_user


@configurator.get("/user/{name}", response_model="json")
async def get_user_by_name(name: str) -> dict:
    for user in users:
        if user["name"] == name:
            return user
    raise HTTPException(404, "User not found")


@configurator.get("/users/{age}", response_model="json")
async def get_users_by_age(age: int) -> list[dict]:
    new_users = []
    for user in users:
        if user["age"] == age:
            new_users.append(user)
    return new_users


if __name__ == "__main__":
    server.run(configurator)
