from unittest import TestCase
import json
import requests

class PatchTest(TestCase):
    def test_user(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {"name": "John", "age": 47}
        data1 = {"age": 47}
        response = requests.patch("http://127.0.0.1:8888/user/John", headers=headers, json=data1)
        self.assertEqual(data, json.loads(response.content))
