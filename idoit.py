#from jsonrpcclient import request
import json
import requests
from pprint import pprint
import getpass

class IdoitServer:
    """Encapsulates a class to interact with i-Doit Server."""

    def __init__(self, username=None, password=None, url=None,):
        self.apikey = input('Please enter API Key: ')
        self.username = input('Enter your cse- username: ')
        self.password = getpass.getpass(prompt='Password: ')
        self.id = 0
        self.url = 'https://cse-app-idoit-dev-01.cse.umn.edu/src/jsonrpc.php'
        self.login_headers = {
            'X-RPC-Auth-Username': self.username,
            'X-RPC-Auth-Password': self.password,
            'content-type': 'application/json',
        }
        self.req_params = {
            'apikey': self.apikey,
            'language': 'en',
        }
        self.raw_payload = {
            'params': self.req_params,
            'jsonrpc': '2.0',
            'id': self.id,
        }
        self.sessionid = self.login()
        self.headers = {
            'content-type': 'application/json',
            'X-RPC-Auth-Session': self.sessionid,
        }
 

    def login(self):
        """Log in to i-Doit server and return session-id."""

        method = {'method': 'idoit.login'}
        payload = json.dumps(self.raw_payload | method)
        response = requests.post(self.url, headers=self.login_headers, data=payload)
        self.id += 1

        return response.json()['result']['session-id']

    def logout(self):
        """Log out of i-Doit."""

        method = {'method': 'idoit.logout'}
        payload = json.dumps(self.raw_payload | method)
        response = requests.post(self.url, headers=self.headers, data=payload)

        print(response.json()['result']['message'])