from unittest import TestCase
import requests
import json

users = [
    {"name": "John", "age": 30},
    {"name": "Jane", "age": 25},
    {"name": "Bob", "age": 40},
    {"name": "Alice", "age": 35},
]
class GetTest(TestCase):
    def test_home(self):
        headers = {
            "Accept": "application/json",
        }
        response = requests.get("http://127.0.0.1:8888/", headers=headers)

        self.assertEqual(users, json.loads(response.content))

    def test_user(self):
        headers = {
            "Accept": "application/json",
        }
        response = requests.get("http://127.0.0.1:8888/user?name=John", headers=headers)

        self.assertEqual(users[0], json.loads(response.content))

    def test_user_not_found(self):
        headers = {
            "Accept": "application/json",
        }
        response = requests.get("http://127.0.0.1:8888/user?name=Tom", headers=headers)

        self.assertEqual(404, response.status_code)


