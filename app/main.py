import datetime
import json, os, requests
from os.path import exists
from time import sleep
from flask import Flask, render_template
from dateutil.parser import *


app = Flask(__name__)


# Homepage
@app.route("/")
def home():
    data = parse()
    failing = data["failing_node_count"]
    passing = data["passing_node_count"]
    total = failing + passing
    failing = round(failing / total * 100)
    passing = round(passing / total * 100)
    return render_template('base.html', failing_nodes=failing, passing_nodes=passing, total=total)

# Failing nodes
@app.route("/failing")
def failing():
    failing_nodes = failing_info()
    return render_template('failing.html', failing=failing_nodes)

@app.route("/failed_node_info/<string:node>", methods=['GET'])
def failed_node_info(node):
    data = failing_info(node)
    return render_template('failed_node_info.html', node=node, failing_nodes_info=data)

@app.route("/all")
def all():
    failed_info = failing_info()
    passed_info = passing_info()
    data = parse()
    failing = data["failing_node_count"]
    passing = data["passing_node_count"]
    total = len(failed_info) + len(passed_info)
    failing = round(failing / total * 100)
    passing = round(passing / total * 100)
    return render_template('all.html', server_total=total, failing_nodes_info=failed_info, passing_nodes_info=passed_info, total_pass=len(passed_info), total_fail=len(failed_info), failing_nodes=failing, passing_nodes=passing)

def parse():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_route = os.path.join(SITE_ROOT, "data", "pe_status.json")
    if exists(json_route):
        # check when the file was last modified
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(json_route))
        now = datetime.datetime.now()
        delta = now - last_modified
        if delta.seconds > 600:
            data = update()
            with open(json_route, 'w') as outfile:
                json.dump(data, outfile)
    else:
        # create the file
        data = update()
        with open(json_route, 'w') as f:
            json.dump(data, f)
            
    json_file = open(json_route, 'r')
    data = json.load(json_file)
    return data

def failing_info(node=""):
    data = parse()
    failed = data["nodes"]["failing"]
    filter_nodes = data["nodes"]["details"]
    return_info = {}
    if len(node) != 0:
        return_info = filter_nodes[node]
    else:
        for filter_node in failed:
            if filter_node in failed:
                return_info[filter_node] = filter_nodes[filter_node]
    return return_info

def passing_info():
    data = parse()
    passing = data["nodes"]["passing"]
    filter_nodes = data["nodes"]["details"]
    nodes_with_passing = {}
    for filter_node in filter_nodes:
        if filter_node in passing:
            nodes_with_passing[filter_node] = filter_nodes[filter_node]
    return nodes_with_passing   

def update():
    host = "https://pe-server-9347bc-0.us-west1-a.c.customer-support-scratchpad.internal:8143"
    url = "{}/orchestrator/v1/command/plan_run".format(host)
    token = "AOBtvBy9wvO-RfmY3pu17EoAFbtjKceYznC_Y3_-O0cC"
    headers = {'X-Authentication': token, 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data='{ "plan_name" : "pe_status_check::infra_summary", "description" : "API call from bart", "params" : { } }', verify=False)

    url = "{}/orchestrator/v1/plan_jobs/{}/events".format(host, response.json()["name"])
    is_finished = False
    while not is_finished:
        response = requests.get(url, headers=headers, verify=False)
        response = json.loads(response.text)
        if len(response["items"]) == 2:
            if response["items"][1]["type"] == "plan_finished":
                is_finished = True
        else:
            sleep(3)
    data = response["items"][1]["details"]["result"]
    return data

if __name__ == "__main__":
    app.run(debug=True)