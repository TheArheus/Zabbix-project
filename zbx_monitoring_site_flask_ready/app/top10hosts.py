#!/usr/bin/python
from pyzabbix import ZabbixAPI
import time
import datetime


def calculate_from_list(list, value_func):
    return_list = []
    reuse = [{"itemid": i['itemid'], "value_avg": float(i['value_avg']), "value_max": float(i['value_max']), "value_min": float(i['value_min'])} for i in list]

    for f in value_func:
        if f == 'value_avg':
            avg_v = sum(i[f] for i in reuse) / len(reuse)
            
        elif f == 'value_max':
            max_v = max(i[f] for i in reuse)
            
        elif f == 'value_min':
            min_v = min(i[f] for i in reuse)
            
        else:
            print("ERROR: no matching function")

    return_list = {"itemid":list[0]['itemid'], "value_avg": avg_v, "value_max": max_v, "value_min": min_v}

    return return_list


class TopHost():
    def __init__(self, zabbix_srv='http://zabbix.rzd/zabbix', login='api_local', passwd="zabbixapi874211"):
        """

        :param zabbix_srv:
        :param login:
        :param passwd:
        """
        self.zbx_server = zabbix_srv
        self.login = login
        self.passwd = passwd

        self.hostname = None
        self.hostgrname = None
        self.key = None
        self.date_from = None
        self.date_till = None

        self.hostid = []
        self.itemid = []

        self.zabbix_conn = ZabbixAPI(self.zbx_server, user=self.login, password=self.passwd)

    def set_filter(self, hostgroups = None, hostname = None, key = None, date_from = None, date_till = None):
        """

        :param hostgoups:
        :param hostname:
        :param key:
        :param date_from:
        :param date_till:
        :return:
        """
        self.hostgrname = hostgroups
        self.hostname = hostname
        self.key = key
        self.date_from = time.mktime(datetime.datetime(date_from.year, date_from.month, date_from.day).timetuple())
        if date_till:
            self.date_till = time.mktime(datetime.datetime(date_till.year, date_till.month, date_till.day).timetuple())
        return self


    def get_history(self, date_from=None, date_till=None):
        """

        :param date_from:
        :param date_till:
        :return:
        """
        list_func = ['value_avg', 'value_max', 'value_min']

        items_history = []
        items_history_res = []

        self.hostid = self.get_hostid(self.hostname)
        item_ids = self.get_items(self.key)


        if self.date_from:
            for id in item_ids:
                items_history.append(
                    self.zabbix_conn.trend.get(itemids=id, time_from=self.date_from,
                                               value_min=True, value_max=True, value_avg=True))

        elif self.date_till:
            for id in item_ids:
                items_history.append(self.zabbix_conn.trend.get(itemids=id, time_till=self.date_till,
                                                                value_min=True, value_max=True,
                                                                value_avg=True))
        elif self.date_from and self.date_till:
            for id in item_ids:
                items_history.append(self.zabbix_conn.trend.get(itemids=id,
                                                                time_from=self.date_from,
                                                                time_till=self.date_till,
                                                                value_min=True, value_max=True,
                                                                value_avg=True))
        elif date_from and date_till:
            for id in item_ids:
                items_history.append(self.zabbix_conn.trend.get(itemids=id,
                                                                time_from=time.mktime(
                                                                    datetime.datetime.strptime(date_from,
                                                                                               '%Y-%m-%d').timetuple()),
                                                                time_till=time.mktime(
                                                                    datetime.datetime.strptime(date_till,
                                                                                               '%Y-%m-%d').timetuple()),
                                                                value_min=True, value_max=True,
                                                                value_avg=True))
        elif date_till:
            for id in item_ids:
                items_history.append(self.zabbix_conn.trend.get(itemids=id, time_till=time.mktime(
                    datetime.datetime.strptime(date_till, '%Y-%m-%d')),
                                                                value_min=True, value_max=True,
                                                                value_avg=True))
        elif date_from:
            for id in item_ids:
                items_history.append(self.zabbix_conn.trend.get(itemids=id, time_from=time.mktime(
                    datetime.datetime.strptime(date_from, '%Y-%m-%d')),
                                                                value_min=True, value_max=True,
                                                                value_avg=True))
        else:
            print("ERROR: you must set date from and date till for filter")
            return []


        for item in items_history:
            if item:
                items_history_res.append(calculate_from_list(item, list_func))

        return items_history_res

    def get_hostgroup(self, names = None, output = None, search=False):
        hostgoups = []

        if output is None:
            output = ['name']

        if names == 'All' or names == 'all':
            hostgoups = self.zabbix_conn.hostgroup.get(name=names, output=output)
        else:
            if names is None:
                for n in self.hostgrname:
                    hostgoups = self.zabbix_conn.hostgroup.get(filter={"name":self.hostgrname}, output=output)
                    # hostgoups = self.zabbix_conn.hostgroup.get(name=self.hostgrname, output=output)

        if output == ['name']:
            names = [n['name'] for n in hostgoups]
            return names
        else:
            return hostgoups


    def get_hostid(self, host_name=None, output='hostid'):
        """

        :param host_name:
        :param output:
        :return:
        """

        if not host_name:
            hosts = self.zabbix_conn.host.get(search={"name": self.hostname}, output=output)
        else:
            hosts = self.zabbix_conn.host.get(search={"name": host_name}, output=output)


        if output == 'hostid':
            hostid = list(h['hostid'] for h in hosts)
            return hostid
        else:
            return hosts

    def get_items(self, key_=None, output='hostid'):
        """

        :param key_: string or array
        :param output: string or array
        :return:
        """

        groups_ids = self.get_hostgroup(output='extend')
        hostgroups_ids = [h['groupid'] for h in groups_ids]

        if not key_:
            items = self.zabbix_conn.item.get(hostids=self.hostid, groupids=hostgroups_ids, with_items=True,
                                              search={'key_': self.key}, startSearch=True, output=output)

        else:
            items = self.zabbix_conn.item.get(hostids=self.hostid, groupids=hostgroups_ids, with_items=True,
                                              search={'key_': key_}, startSearch=True, output=output)


        if output == 'hostid':
            itemid = list(i['itemid'] for i in items)
            return itemid
        else:
            return items

