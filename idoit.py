import json
import requests
from pprint import pprint
from idoit import HOST_TYPE_DICT
import getpass
import sys

class SearchError(Exception):
    """Raise when something can't be found."""

class IdoitServer:
    """Encapsulates a class to interact with i-Doit Server."""

    def __init__(self, apikey=None, username=None, password=None, url=None,):
        self.apikey = apikey or input('Please enter API Key: ')
        self.username = username or input('Enter your cse- username: ')
        self.password = password or getpass.getpass(prompt='Password: ')
        if url is None or url == 'dev':
            self.url = 'https://cse-app-idoit-dev-01.cse.umn.edu/src/jsonrpc.php'
        elif url =='prd':
            self.url = 'https://cse-app-idoit-prd-01.cse.umn.edu/src/jsonrpc.php'
        else:
            raise ValueError('Either input no URL or dev for Dev, otherwise input prd for Production.')
        self.login_headers = {
            'X-RPC-Auth-Username': self.username,
            'X-RPC-Auth-Password': self.password,
            'content-type': 'application/json',
        }
        self.req_params = {
            'apikey': self.apikey,
            'language': 'en',
        }
        self.id = 0
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

        response = requests.post(self.url, headers=self.login_headers, data=json.dumps({**self.raw_payload, **method}))
        response.raise_for_status()
        self.id += 1

        try:
            return response.json()['result']['session-id']
        except KeyError:
            print('Login failed!')
            sys.exit(-1)


    def logout(self):
        """Log out of i-Doit."""

        method = {'method': 'idoit.logout'}

        response = requests.post(self.url, headers=self.headers, data=json.dumps({**self.raw_payload, **method}))
        response.raise_for_status()
        self.id+=1

        print(response.json()['result']['message'])
    

    def constants(self):
        """Fetch defined constants from i-doit."""

        method = {'method': 'idoit.constants'}

        response = requests.post(self.url, headers=self.headers, data=json.dumps({**self.raw_payload, **method}))
        response.raise_for_status()
        self.id+=1

        return pprint(response.json())


    def search(self, object_name):
        """Search for a particular object and return object id."""

        query = {'q': object_name}

        search_params = {**self.req_params, **query}
        search_payload = {
            'method': 'idoit.search',
            'params': search_params,
            'jsonrpc': '2.0',
            'id': self.id,
        }

        try:
            response = requests.post(self.url, headers=self.headers, data=json.dumps(search_payload))
            response.raise_for_status()
            self.id+=1
            return response.json()['result'][0]['documentId']
        except IndexError:
            raise SearchError(f'{object_name} can\'t be found.')


    def read(self, object_name):
        """Read common information about an object."""
    
        id = self.search(object_name)

        query = {'id': id}
        search_params = {**self.req_params, **query}

        search_payload = {
            'method': 'cmdb.object.read',
            'params': search_params,
            'jsonrpc': '2.0',
            'id': self.id,
        }
        
        response = requests.post(self.url, headers=self.headers, data=json.dumps(search_payload))
        response.raise_for_status()
        self.id+=1

        pprint(response.json())
    

    def create_os(self, os_name):
        """Create new os object with some optional information."""

        os_params = {
            'type': 'C__OBJTYPE__OPERATING_SYSTEM',
            'title': os_name,
        }

        post_params = {**self.req_params, **os_params}

        post_payload = {
            'method': 'cmdb.object.create',
            'params': post_params,
            'jsonrpc': '2.0',
            'id': self.id,
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(post_payload))
        response.raise_for_status()
        self.id+=1

        pprint(response.json())
    

    def create_vm(self, vm_name):
        """Create a new VM type object with some optional information."""

        # First check if the VM exists,
        try:
            self.search(vm_name)
            vm_exists = True
            return ValueError('This machine already exists!')
        except SearchError:
            pass

        vm_params = {
            'type': 'C__OBJTYPE__VIRTUAL_SERVER',
            'title': vm_name,
        }

        post_params = {**self.req_params, **vm_params}

        post_payload = {
            'method': 'cmdb.object.create',
            'params': post_params,
            'jsonrpc': '2.0',
            'id': self.id,
        }


        response = requests.post(self.url, headers=self.headers, data=json.dumps(post_payload))
        response.raise_for_status()
        self.id+=1

        pprint(response.json())


        def create_host(self, vm_name):
            """Create a new host type object with some optional information."""

        # First check if the VM exists,
        try:
            self.search(vm_name)
            vm_exists = True
            return ValueError('This machine already exists!')
        except SearchError:
            pass

        vm_params = {
            'type': 'C__OBJTYPE__VIRTUAL_SERVER',
            'title': vm_name,
        }

        post_params = {**self.req_params, **vm_params}

        post_payload = {
            'method': 'cmdb.object.create',
            'params': post_params,
            'jsonrpc': '2.0',
            'id': self.id,
        }


        response = requests.post(self.url, headers=self.headers, data=json.dumps(post_payload))
        response.raise_for_status()
        self.id+=1

        pprint(response.json())


    def update_host_os(self, hostname, os):
        """Assign an OS to a VM."""

        try:
            hostID = self.search(hostname)
            osID = self.search(os)
        except IndexError:
            print(f'{os} or {hostname} not found!')

        vm_os_params = {
            'objID': int(hostID),
            'data': {
                'application': int(osID),
            },
            'catgID': 'C__CATG__OPERATING_SYSTEM',
        }
        post_params = {**self.req_params, **vm_os_params}

        post_payload = {
            'method': 'cmdb.category.create',
            #'method': 'cmdb.category.save',
            'params': post_params,
            'jsonrpc': '2.0',
            'id': self.id,
        }
        #import pdb; pdb.set_trace()

        response = requests.post(self.url, headers=self.headers, data=json.dumps(post_payload))
        response.raise_for_status()
        self.id+=1

        pprint(response.json())