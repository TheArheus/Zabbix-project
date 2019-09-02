#!/usr/bin/python
from pyzabbix import ZabbixAPI
import random
import sys

ZABBIX_SERVER = 'http://zabbix.rzd/zabbix'
login='api_local'
passwd="zabbixapi874211"
h_keys = []
keys = []
graphitem = []
gtype = 0 # Default graph type normal (posible valie is 1 for stacked).
         #It can be defined by not required parameter for graphtype

if len(sys.argv) == 1:
    print("ERROR: missed required parameters. You should pass hostname and key parameters")
    sys.exit(1)
elif len(sys.argv) == 2:
    print("ERROR: missed one of required parameter. You should pass hostname or key missed parameter")
    sys.exit(1)

hostname = sys.argv[1]
key = sys.argv[2]

if len(sys.argv) == 4:
    if sys.argv[3] == "normal":
        gtype = 0
    elif sys.argv[3] == "stacked":
        gtype = 1
    else:
        print("ERROR: you should pass 'normal' or 'stacked' for graph type ")

if len(sys.argv) > 4:
    print("ERROR: there are only two required and one non required parameters")
    sys.exit(1)

graph_name = 'all {}'.format(key)


def get_Color(elements):
    r = lambda: random.randint(0, 255)
    colors = ['%02X%02X%02X' % (r(),r(),r()) for c in range(0, elements)]
    return colors

try:
    zabbix_conn = ZabbixAPI(ZABBIX_SERVER)
    zabbix_conn.login(login, passwd)
except:
    print('ERROR: unable to connect to ZABBIX server. Wrong login or password')
    sys.exit(1)

try:
    hosts = zabbix_conn.host.get(filter={"host": hostname}, output=["hostid"])
    hostid = hosts[0]['hostid']
except:
    print('ERROR: cannot get given host {}'.format(hostname))
    sys.exit(1)


try:
     h_keys = zabbix_conn.item.get(hostids=hostid, filter={'flags': 4}, search={'key_': key}, startSearch=True, output=["key_", "name"])
except:
    print('ERROR: cannot get any item for given host id{}'.format(hostid))
    sys.exit(1)

keys = [h['itemid'] for h in h_keys]

color = get_Color(len(keys))

graphitem = [{'itemid': item, 'color': c, 'calc_fnc': 4} for item, c in zip(keys, color)]

try:
    graph = zabbix_conn.graph.get(hostids=hostid, filter={"name": graph_name}, output="graphid")
except:
    print('ERROR: unable to get any graph for host id{}'.format(hostid))
    sys.exit(1)

if graph:
    try:
        zabbix_conn.graph.update(graphid=graph[0]['graphid'], gitems=graphitem)
    except Exception as err:
        print('ERROR: cannot update graph ({})'.format(err))
        sys.exit(1)
    print('OK: graph id {} updated successfully'.format(graph[0]['graphid']))
else:
    try:
        zabbix_conn.graph.create(name=graph_name, height=200, width=900, graphtype=gtype, gitems=graphitem)
    except Exception as err:
        print('ERROR: cannot create graph ({})'.format(err))
        sys.exit(1)
    print('OK: graph created successfully')
