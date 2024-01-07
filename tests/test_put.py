from unittest import TestCase
import json
import requests

class PutTest(TestCase):
    def test_user(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {"name": "John", "age": 32}
        response = requests.put("http://127.0.0.1:8888/user/John", headers=headers, json=data)
        self.assertEqual(data, json.loads(response.content))
