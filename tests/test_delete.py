from unittest import TestCase
import json
import requests

class DeleteTest(TestCase):
    def test_user(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {"name": "Max", "age": 19}
        requests.post("http://127.0.0.1:8888/user", headers=headers, json=data)
        response = requests.delete("http://127.0.0.1:8888/user/Max", headers=headers)
        self.assertEqual(response.status_code, 204)
