#!/usr/bin/python
import sys
from pyzabbix import ZabbixAPI
from pprint import pprint
import time
import datetime
import json

def func(list, value_func):
    return_list = []
    reuse = [{"itemid": i['itemid'], "value_avg": float(i['value_avg']), "value_max": float(i['value_max']), "value_min": float(i['value_min'])} for i in list]

    for f in value_func:
        if f == 'value_avg':
            avg_v = sum(i[f] for i in reuse) / len(reuse)
            pass
        elif f == 'value_max':
            max_v = max(i[f] for i in reuse)
            pass
        elif f == 'value_min':
            min_v = min(i[f] for i in reuse)
            pass
        else:
            pprint("ERROR: no matching function")

    return_list = {"itemid":list[0]['itemid'], "value_avg": avg_v, "value_max": max_v, "value_min": min_v}

    return return_list


if len(sys.argv) == 1:
    print("ERROR: missed required parameters. You should pass hostname and key parameters")
    sys.exit(1)
elif len(sys.argv) == 2:
    print("ERROR: missed one of required parameter. You should pass hostname or key missed parameter")
    sys.exit(1)

items = []
hosts = []
items_history = []
items_history_res = []

hostname = sys.argv[1]
key = sys.argv[2]
date_from = time.mktime(datetime.datetime.strptime(sys.argv[3], "%d/%m/%Y").timetuple())
#date_to = time.mktime(datetime.datetime.strptime(sys.argv[4], "%d/%m/%Y").timetuple())

ZABBIX_SERVER = 'http://zabbix.rzd/zabbix'
login = 'api_local'
passwd = "zabbixapi874211"
list_of_names = ['value_avg', 'value_max', 'value_min']

try:
    zabbix_conn = ZabbixAPI(ZABBIX_SERVER, user='artem', password='metra')
except:
    print('ERROR: unable to connect to ZABBIX server. Wrong login or password')
    sys.exit(1)

try:
    hosts = zabbix_conn.host.get(search={"host": hostname}, output=['hostid'])
    hostid = list(h['hostid'] for h in hosts)
except Exception as e:
    print("ERROR: {}".format(e))
    sys.exit(1)

try:
    items = zabbix_conn.item.get(hostids=hostid, with_items=True, search={'key_': key}, startSearch=True, output='hostid')
    item_ids = list(i['itemid'] for i in items)
except Exception as e:
    print("ERROR: {}".format(e))
    sys.exit(1)

try:
    for id in item_ids:
        items_history.append(zabbix_conn.trend.get(itemids=id, time_from=date_from, value_min=True, value_max=True, value_avg=True))
except Exception as e:
    print("ERROR: {}".format(e))
    sys.exit(1)


for item in items_history:
    if item:
        items_history_res.append(func(item, list_of_names))



