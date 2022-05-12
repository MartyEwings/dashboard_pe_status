import json, os
from readline import parse_and_bind
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
    data = parse()
    failed = data["nodes"]["failing"]
    filter_nodes = data["nodes"]["details"]
    new_dic = {}
    for filter_node in filter_nodes:
        if filter_node in failed:
            new_dic[filter_node] = filter_nodes[filter_node]
    return render_template('failing.html', failing=new_dic)

# @app.route("/passing")
# def failing():
#     data = parse()
#     passing = data["nodes"]["passing"]
    
#     return render_template('passing.html', passing=passing)

@app.route("/all")
def all():
    data = parse()
    failing = data["nodes"]["failing"]
    passing = data["nodes"]["passing"]
    return render_template('all.html', failing_nodes=failing, passing_nodes=passing)

def parse():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_route = os.path.join(SITE_ROOT, "data", "pe_status.json")
    json_file = open(json_route, 'r')
    data = json.load(json_file)
    return data

# def failing_info(fqdn):
#     data = parse()
#     failed_info = []
#     if data["details"] == fqdn:
#         failed_info.append(data["details"]["failed_tests_detials"])
#     return failed_info

if __name__ == "__main__":
    app.run(debug=True)