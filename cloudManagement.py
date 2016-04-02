#     Author: Alessandro Zanni
#     URL: https://github.com/AleDanish

from heatclient.client import Client
import keystoneclient.v2_0.client as ksclient

tenant_name='mcntub'
tenant_id='64969ad482c643cb8439a55e648e5ebb'
heat_url='http://bart.cloudcomplab.ch:8004/v1/' + tenant_id
auth_url="http://bart.cloudcomplab.ch:5000/v2.0"
username="alessandropernafini"
password="unib0bart"

class CloudOrchestrator():
    def __init__(self):
        self.auth_token = self.get_auth_token()
        heat = Client('1', endpoint=heat_url, token=self.auth_token)
        self.stack_manager = heat.stacks        
        self.stack_id = self.get_stack_id()
        self.stack_list = []
        self.auth_token = self.get_auth_token()

    def get_stack_list(self):
        if self.stack_manager is None:
            self.__init__(self.auth_token)
        stack_generator = self.stack_manager.list()
        self.stack_list = [x for x in stack_generator]
        return self.stack_list

    def get_stack(self):
        if self.stack_id is None:
            self.get_stack_id()
        if not self.stack_list:
            self.stack_list = self.get_stack_list()
        for stack in self.stack_list:
            if stack.id == self.stack_id:
                return stack
        return None

    def get_auth_token(self):
        keystone = ksclient.Client(auth_url=auth_url, username=username, password=password, tenant_name=tenant_name)
        token = keystone.auth_ref['token']['id']
        self.auth_token = token
        return token
#        self.auth_token = open('/home/ubuntu/authtoken', 'r').read().rstrip()
#        return self.auth_token

    def get_stack_id(self):
        self.stack_id = open('/home/ubuntu/stackid', 'r').read().rstrip()
        return self.stack_id

    def create_stack(self, params):
        if self.stack_manager is None:
            self.__init__(self.auth_token)
        self.stack_manager.create()

    def delete_stack(self):
        if self.stack_id is None :
            self.stack_id = self.get_stack_id()
        self.stack_manager.delete(self.stack_id)
