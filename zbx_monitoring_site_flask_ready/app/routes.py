from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField

from app import app
from app import forms
from app import top10hosts

from pprint import pprint


top_hosts_obj = top10hosts.TopHost()

func = ['value_avg', 'value_max', 'value_min']
values = []

hostgroups = top_hosts_obj.get_hostgroup(names='All')
hostgroup_select = [(g, g) for g in hostgroups]


class selectGr(FlaskForm):
    host_group = SelectMultipleField("Host Groups", choices=hostgroup_select)


@app.route("/", methods=['GET', 'POST'])
@app.route("/monitor", methods=['GET', 'POST'])
@app.route("/monitor/", methods=['GET', 'POST'])
def index():
    form = forms.filter()
    select_form = selectGr()

    if form.validate_on_submit():
        top_hosts_obj.set_filter(hostgroups=select_form.host_group.data, hostname=form.host_name.data,
                                 key=str(form.key.data), date_from=form.date_from.data, date_till=form.date_till.data)

        values = top_hosts_obj.get_history()
        keys = top_hosts_obj.get_items(str(form.key.data), ['key_', 'itemid', 'hostid'])
        hosts = top_hosts_obj.get_hostid(output=['hostid', 'host'])
        
        return render_template("render_file.html", form=form, select_form=select_form, values=values, keys=keys, hosts=hosts)

    return render_template("render_file.html", form=form, select_form=select_form)