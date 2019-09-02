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

        if not form.host_name.data:
            return redirect(url_for('index', val1=select_form.host_group.data, val2=None,
                                    val3=form.key.data, val4=form.date_from.data, val5=form.date_till.data))
        else:
            return redirect(url_for('index', val1=select_form.host_group.data, val2=form.host_name.data,
                                    val3=form.key.data, val4=form.date_from.data, val5=form.date_till.data))

    return render_template("render_file.html", form=form, select_form=select_form)

@app.route("/monitor/<val1>/<val2>/<val3>/<val4>/<val5>", methods=['GET', 'POST'])
def index1(val1=None, val2=None, val3=None, val4=None, val5=None):
    form = forms.filter()
    select_form = selectGr()

    return render_template("render_file.html", form=form, select_form=select_form, values=values,
                           val1=val1, val2=val2, val3=val3, val4=val4, val5=val5)