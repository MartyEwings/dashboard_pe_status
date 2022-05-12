import json, os, logging
from queue import Empty
from flask import Flask, render_template


app = Flask(__name__)

# Homepage
@app.route("/")
def home():
    data = parse()
    failing = data["failing_node_count"]
    passing = data["passing_node_count"]
    return render_template('base.html', failing_nodes=failing, passing_nodes=passing)

# Failing nodes
@app.route("/failing")
def failing():
    failing_nodes = failing_info()
    return render_template('failing.html', failing=failing_nodes)

@app.route("/failed_node_info/<string:node>", methods=['GET'])
def failed_node_info(node):
    data = failing_info(node)
    app.logger.error(data)
    return render_template('failed_node_info.html', node=node, failing_nodes_info=data)

@app.route("/all")
def all():
    failed_info = failing_info()
    passed_info = passing_info()
    total = len(failed_info) + len(passed_info)
    return render_template('all.html', server_total=total, failing_nodes_info=failed_info, passing_nodes_info=passed_info, total_pass=len(passed_info), total_fail=len(failed_info), total_pass_percentage=round(len(passed_info)/total*100, 2), total_fail_percentage=round(len(failed_info)/total*100, 2))

def parse():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_route = os.path.join(SITE_ROOT, "data", "pe_status.json")
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

if __name__ == "__main__":
    app.run(debug=True)