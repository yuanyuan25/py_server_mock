#/usr/bin/env python

import json
import os
import time
import traceback
import requests
from flask import Flask,redirect, url_for, request, render_template, jsonify
from urllib.parse import urlencode
app = Flask(__name__)

# os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class Cache(object):
    def __init__(self):
        self.cache_path = "mock_data"
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
        self.cache_data = self.init_cache()

    def init_cache(self):
        cache_data = {}
        for file in os.listdir(self.cache_path):
            with open(os.path.join(self.cache_path, file), 'r') as f:
                cache_data[file] = json.loads(f.read())
        return cache_data

    def set(self, key, value):
        if key == "" or value == "":
            print(f"key or value is empty")
            return
        with open(os.path.join(self.cache_path, key), 'w') as f:
            print(f"set key: {key}, value: {value}")
            f.write(json.dumps(value, ensure_ascii=False))
    
    def get_all_keys(self):
        list = os.listdir(self.cache_path)
        return list

    def get(self, key):
        if key == "":
            print(f"key is empty")
            return ""
        if key in self.cache_data:
            print(f"get key from cache: {key}, value: {self.cache_data[key]}")
            return self.cache_data[key]

        with open(os.path.join(self.cache_path, key), 'r') as f:
            print(f"get key from file: {key}")
            return json.loads(f.read())

cache = Cache()
@app.route('/', methods=["GET"])
def index():
    return redirect('/mock/search')

@app.route('/mock', methods=["GET"])
def mock():
    return redirect('/mock/search')

@app.route('/mock/get', methods=["GET"])
def get():
    try:
        args = request.args
        print(f"mock get")
        api_name = args.get('api_name', "")
        mock_data = cache.get(api_name)
        out = mock_data
    except Exception as e:
        print(f"error: {repr(e)}")
        out = {"state": 1, "error_msg": repr(e)}
    return out
   
@app.route('/mock/search', methods=["GET"])
def search():
    args = request.args
    print(f"mock get")
    api_name = args.get('api_name', "")
    mock_value = cache.get(api_name)
    api_list = cache.get_all_keys()
    print(api_name)
    print(mock_value)
    print(api_list)
    out = {"status":0, "msg":"success", "api_name":api_name, "mock_value": json.dumps(mock_value, ensure_ascii=False), "api_list": api_list}
    return render_template("search_mock.html", mock=out)
   
@app.route('/mock/set', methods=['POST',"GET"])
def set():
    try:
        if request.method == 'POST':
            print(f"post mock set")
            args = request.form
            # print(args)
            api_name = args.get('api_name', "")
            mock_value = args.get('mock_value', "")
            mock_data = ""
            if mock_value != "":
                mock_data = json.loads(mock_value)
            print(api_name)
            print(mock_data)
            cache.set(api_name, mock_data)
            out = {"status":0, "msg":"success", "api_name":api_name, "mock_value": mock_value}
        else:
            out = {"status":0, "msg":"", "api_name":"", "mock_value": ""}
    except Exception as e:
        traceback.print_exc()
        print(f"error: {repr(e)}")
        out = {"state": 1, "msg": "failed:"+repr(e), "api_name":"", "mock_value": ""}
    return render_template("set_mock.html", mock=out)
   
if __name__ == '__main__':
      app.run(debug=False, port=18000, host='0.0.0.0')
