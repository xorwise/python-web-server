from unittest import TestCase
import json
import requests

class PostTest(TestCase):
    def test_user(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {"name": "Mike", "age": 32}
        response = requests.post("http://127.0.0.1:8888/user", headers=headers, json=data)
        self.assertEqual(data, json.loads(response.content))
