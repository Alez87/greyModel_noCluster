#     Author: Alessandro Zanni
#     URL: https://github.com/AleDanish

from heatclient.client import Client
import keystoneclient.v2_0.client as ksclient
from heatclient.common import template_utils
from heatclient.exc import HTTPConflict
from heatclient.common import utils
import time

tenant_name='mcntub'
tenant_id='64969ad482c643cb8439a55e648e5ebb'
heat_url='http://bart.cloudcomplab.ch:8004/v1/' + tenant_id
keystone_credentials = {
    'username': 'alessandropernafini',
    'password': 'unib0bart',
    'tenant_name': 'mcntub',
    'auth_url': 'http://bart.cloudcomplab.ch:5000/v2.0'
}
stack_name="teststack-influxdb-cyclops"
template_file="data/influxdb-cyclops.yaml"

class HeatClient():
    def __init__(self, region_name):
        self.region_name = region_name
        self.auth_token = self.get_auth_token()
        heat_credentials = {
            'endpoint': heat_url,
            'token': self.auth_token,
            'service_type': 'orchestration',
            'endpoint_type': 'publicURL',
            'region_name': 'RegionOne'
        }
        heat = Client('1', **heat_credentials)
        self.stack_manager = heat.stacks
        self.stack_id = None
        self.stack_id = self.get_stack_id()
        self.stack_list = []
        self.auth_token = self.get_auth_token()
        self.floating_ip = None
        self.floating_ip = self.get_floating_ip()

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
        keystone = ksclient.Client(**keystone_credentials)
        token = keystone.auth_ref['token']['id']
        self.auth_token = token
        return token

    def get_stack_id(self):
        if self.stack_id is None:
            self.stack_id = open('/home/ubuntu/stackid', 'r').read().rstrip() 
        return self.stack_id

    def get_floating_ip(self):
        if self.floating_ip is None:
            try:
                self.floating_ip = open('/home/ubuntu/influxdb_floatingip', 'r').read().rstrip()
            except IOError:
                self.floating_ip = None
                print "Warning: no influxdb_floatingip found"
        return self.floating_ip

    def create_stack(self):
        Tcreate_stack_start=time.time()

        if self.stack_manager is None:
            self.__init__(self.auth_token)
        tpl_files, template = template_utils.get_template_contents(template_file)
        stack = None
        stack_number = 0
        stack_created = False
        while stack_created == False:
            stack_number += 1
            try:
                stack_name_full = stack_name + str(stack_number)
                print "stack name: ", stack_name_full
                kwargs = None
                float_ip = self. get_floating_ip()
                if float_ip:
                    params = ['influxdb_floating_ip_old=' + float_ip]
                    kwargs = {
                       'stack_name': stack_name_full,
                       'template': template,
                       'parameters': utils.format_parameters(params)
                    }
                else:
                    kwargs = {
                       'stack_name': stack_name_full,
                       'template': template
                    }
                self.stack_manager.validate(**kwargs)
                stack=self.stack_manager.create(**kwargs)
                print "stack: ", stack
                uid=stack['stack']['id']
                self.stack_id = uid
                stack=self.stack_manager.get(stack_id=uid).to_dict()
                while stack['stack_status'] == 'CREATE_IN_PROGRESS':
                    print "Stack in state: {}".format(stack['stack_status'])
                    stack = self.stack_manager.get(stack_id=uid).to_dict()
                    time.sleep(5)
                if stack['stack_status'] == 'CREATE_COMPLETE':
                    print "Stack succesfully created."
                else:
                    raise Exception("Stack fall to unknow status: {}".format(stack))
                stack_created = True
            except HTTPConflict:
                print "Stack ", stack_name_full, " already exists"

        Tcreate_stack=time.time()-Tcreate_stack_start
        print "Time to create the new stack: ", Tcreate_stack, "s"

        return stack

    def delete_stack(self):
        if self.stack_id is None:
            self.stack_id = self.get_stack_id()
        self.stack_manager.delete(self.stack_id)
