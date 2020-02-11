from flask import Flask, request, jsonify, Response, render_template
import json
import requests
import os
import sys
from sesamutils import VariablesConfig, sesam_logger
import pandas as pd
import urllib3
from itertools import groupby
from operator import itemgetter
import numpy as np
import urllib.request, json
from jsonpath_ng import jsonpath, parse
import hashlib



app =Flask(__name__)
logger = sesam_logger("Steve the logger", app=app)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#required_env_vars = ['jwt','base_url']

def get_data(path):
    with urllib.request.urlopen(path) as url:
        data = json.loads(url.read().decode())
    return data

def flatten_json(nested_json):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:

                flatten(x[a], name + a + '_')

        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name)

                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out



def build_dict(paths):
    if len(paths) == 1 and len(paths[0]) == 1:
        return {"name": paths[0][0]}
    dirname = paths[0][0]
    d = {"name": dirname, "children": []}
    for k, g in groupby(sorted([p[1:] for p in paths], key=itemgetter(0)),
                        key=itemgetter(0)):
        d["children"].append(build_dict(list(g)))
    return d


def hash_col(col):
    h = hashlib.new('sha256')
    h.update('{}'.format(col).encode('utf-8'))

    return  h.hexdigest()

def hash_marked_values(hashed_values):
    global data
    print(hashed_values)
    for key,values in hashed_values.items():
        if len(values) == 1:
            data[key] = hash_col(data[key])

        else:
            main_val = key
            parser = ('.[*].').join(list(reversed(values))[:-1]) + str('.[*]')
            jsonpath_expr = parse(parser)

            for i,x in enumerate(jsonpath_expr.find(data)):
                try:
                    jsonpath_expr.find(data)[i].value[main_val] = hash_col(x.value[main_val])
                except:
                    continue

    #Returs data to Sesam
    print(data)
    return data

@app.route('/file/<path:path>')
def index(path):

    global data

    url = path
    data = get_data(path)
    unique_tree = sorted(np.unique(np.array([['root'] + x.split('_') for x in list(flatten_json(data).keys())])),key=len)
    output = [build_dict(unique_tree)]


    return render_template('index.html',tree_data=output)

@app.route('/hash/<hashedvalues>', methods=['GET'])
def hasheddata(hashedvalues):

    jsonrespons = hash_marked_values(hashedvalues)

    requests.put(f"{config.base_url}/pipes/{pipe_id}/config?force=True", headers=header, data=json.dumps(new_source), verify=False)

    return data



@app.route('/hash', methods=['POST'])
def hash():

    hashed_values = request.get_json()
    hash_marked_values(hashed_values)

    #POST to sesam API with hashed values as some data

    return 'Success!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
