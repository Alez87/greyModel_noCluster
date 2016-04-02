import json
import requests

class APIConnector():
    def __init__(self):
	self.user = 'azanni'
	self.pwd = 'azanni'
        self.url = 'http://137.204.57.236:8008/zabbix/api_jsonrpc.php'
        self.token = None
        self.hosts = None

    def auth_zabbix(self):
        headers = {'Content-type': 'application/json'}
        data = {
            "jsonrpc": "2.0",
            "method": "user.authenticate",
            "id": 1,
            "params": {
                "user": self.user,
                "password": self.pwd
            }
        }
        data = json.dumps(data)
        response = requests.post(self.url, data, headers=headers).json()
        self.token = response["result"]
        return response["result"]

    def get_zbx_hostids(self):
        headers = {'Content-type': 'application/json'}
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "id": 1,
            "params": {
                "sortfield": "name",
                "output": ["hostid", "name"]
            },
            "auth": self.token
        }
        data = json.dumps(data)
        response = requests.post(self.url, data, headers=headers).json()
        self.hosts = response["result"]
        return response["result"]

    def get_zbx_items(self, search_string, host_ids):
        headers = {'Content-type': 'application/json'}
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "id": 1,
            "params": {
                "sortfield": "name",
                "output": ["key_", "name", "lastvalue", "itemid"],
                "hostids": host_ids,
                "search": {
                    "key_": search_string
                }
            },
            "auth": self.token
        }
        data = json.dumps(data)
        response = requests.post(self.url, data, headers=headers).json()
        return response["result"]

    def get_cpu_load(self):
        if self.hosts is None:
            self.hosts = self.get_zbx_hostids()
        values = []
        for host in self.hosts:
            cpu_load = 0
            for item in self.get_zbx_items('cpu', host['hostid']):
                if item["key_"] == "system.cpu.load[percpu,avg1]":
                    cpu_load = float(item['lastvalue']) * 100
                    values.append(float("{0:.4f}".format(cpu_load)))
                    #print "cpu load:", str(load * 100)+"% on host:",host
        return values

    def get_cpu_util(self):
        if self.hosts is None:
            self.hosts = self.get_zbx_hostids()
        values = []
        for host in self.hosts:
            cpu_util = 0
            for item in self.get_zbx_items('cpu', host['hostid']):
                if item["key_"] == "system.cpu.util[,idle]":
                    cpu_util = 100 - float(item['lastvalue'])
                    values.append(float("{0:.4f}".format(cpu_util)))
                    #print "cpu util:", str(cpu_util * 100)+"% on host:",host
        return values

    def get_mem_load(self):
        if self.hosts is None:
            self.hosts = self.get_zbx_hostids()
        values = []
        for host in self.hosts:
            mem_free = 0
            for item in self.get_zbx_items('memory', host['hostid']):
                if "total" in item['key_']:
                    mem_total = float(item['lastvalue'])
                elif "available" in item['key_']:
                    mem_available = float(item['lastvalue'])
            mem_free = mem_available/mem_total
            values.append(float("{0:.4f}".format(mem_free * 100)))
            #print "free memory: {0:.2f}%".format(mem_free * 100)+"% on host:",host
        return values
