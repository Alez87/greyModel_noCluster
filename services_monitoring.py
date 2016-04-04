#     Author: Alessandro Zanni
#     URL: https://github.com/AleDanish

from py4j.java_gateway import JavaGateway
from py4j.java_collections import SetConverter, MapConverter, ListConverter
import time
import random
import thread
from zabbix_api import APIConnector
from heat_client import HeatClient
import sys

#For monitoring purpose
import time
import paramiko

zabbix_url='http://137.204.57.236:8008/zabbix/'
zabbix_user='azanni'
zabbix_pass='azanni'
trigger_value=0.5

class MyList(list):
    def append(self, item):
        list.append(self, item)        
        if len(self) > 5: self[:1]=[]

def getGreyModelValues(composedList):
    values = []
    for list_py in composedList:
        list_java = ListConverter().convert(list_py, gateway._gateway_client)
        nextValue = gateway.entry_point.nextValue(list_java)
        values.append(float("{0:.4f}".format(nextValue)))
    return values

def moveVM():
    migrationVM = True
    co_old = HeatClient(None)
    
    region_new = "RegionOne"
    co_new = HeatClient(region_new)
    stack = co_new.create_stack()
    print "stack_new: ", stack
   
    old_ip=stack['parameters']['influxdb_floating_ip_old']
    new_ip_raw=stack['outputs'][0]['output_value']
    new_ip=re.findall( r'[0-9]+(?:\.[0-9]+){3}', new_ip_raw)[0]
    print "old VM ip: ", old_ip
    print "new VM ip: ", new_ip

    if not old_ip or not new_ip:
        print "Cannot move data. Missing IP"
        print "old VM ip: ", old_ip
        print "new VM ip: ", new_ip
    else:
        print "I'm moving data..."
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(new_ip, username='ubuntu', key_filename='/home/ubuntu/key/mcn-key.pem')
        command = 'bash /home/ubuntu/greyModel_noCluster/database_config.sh ' + old_ip
        stdin, stdout, stderr = ssh.exec_command(command)
        print "Script output", stdout.readlines()
        ssh.close()
        print "Data moved"

#    TODO:
#   co_old.delete_stack()
    migrationVM = False

Tstart=time.time()
migrationVM = False
gateway = JavaGateway()
connector = APIConnector()
auth = connector.auth_zabbix()
host_ids = connector.get_zbx_hostids()
hosts_cpu_load = []
hosts_cpu_util = []
hosts_mem = []
for host in host_ids:
    hosts_cpu_load.append(MyList())
    hosts_cpu_util.append(MyList())
    hosts_mem.append(MyList())

Tconfig=time.time()-Tstart
print "Config time: ", Tconfig, "s"

while True:
    Tzbx_start=time.time()

    cpu_loads = connector.get_cpu_load()
    cpu_util = connector.get_cpu_util()
    mem = connector.get_mem_load()
    for i in range(len(host_ids)):
        hosts_cpu_load[i].append(cpu_loads[i])
        hosts_cpu_util[i].append(cpu_util[i])
        hosts_mem[i].append(mem[i])
    print "zbx - cpu_load: ", hosts_cpu_load
    print "zbx - cpu_util: ", hosts_cpu_util
    print "zbx - mem: ", hosts_mem

    Tzbx=time.time()-Tzbx_start
    print "Zbx time to read: ", Tzbx, "s"

    if len(hosts_cpu_load[0]) > 0:
        Tgm_start=time.time()

        cpu_load_GM = getGreyModelValues(hosts_cpu_load)
        cpu_util_GM = getGreyModelValues(hosts_cpu_util)
        mem_GM = getGreyModelValues(hosts_mem)
        print "next value GM - cpu_load: ", cpu_load_GM
        print "next value GM - cpu_util: ", cpu_util_GM
        print "next value GM - mem: ", mem_GM

        Tgm=time.time()-Tgm_start
        print "Time to get Grey Model value: ", Tgm, "s"

        avg=reduce(lambda x, y: x + y, cpu_load_GM)/len(cpu_load_GM)
        print avg
        if (avg > trigger_value) and (migrationVM == False):
            print "Trigger activated. I'm going to move the VM state."
            try:
                Tmovetot_start=time.time()
                moveVM()
                Tmovetot=time.time()-Tmovetot_start
                print "Total time to migrate the VMs: ", Tmovetot, "s"
            except:
                print "Cannot move VM. Unexpected error:", sys.exc_info()[0]
                raise
    time.sleep(5)
