import json
from unittest import TestCase
import requests


class ParametersTest(TestCase):

    def test_parameter(self):
        url = "http://127.0.0.1:8888/user/John"
        user = {"name": "John", "age": 30}
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers)
        self.assertEqual(response.json(), user)

    def test_parameters_conversion(self):
        url = "http://127.0.0.1:8888/users/30"
        users = [{"name": "John", "age": 30}]
        headers = {"Accept": "application/json"}

        response = requests.get(url, headers)
        self.assertEqual(response.json(), users)

    def test_parameters_conversion_error(self):
        url = "http://127.0.0.1:8888/users/abc"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers)
        self.assertEqual(response.status_code, 422)
