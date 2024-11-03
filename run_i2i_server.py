#/usr/bin/env python

import json
import os, sys
sys.path.append("../i2i/xbert-final/code")
sys.path.append("../faiss")
import time
#from NER.BERT_CRF_PROPERTY.named_entity_recognition import init_online_model as ner_init_model, predict_online as ner_predict
from bert_embedding import init_online_model,  predict_online 
from faiss_search import FaissSearch
from config import config
import requests
from flask import Flask,redirect, url_for, request
from urllib.parse import urlencode
app = Flask(__name__)

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class I2I(object):
    def __init__(self):
        self.model, self.args, self.tokenizer, self.processor = init_online_model(config['model_path'])

    def predict(self, text_list):
        output = predict_online(self.model, self.args, self.tokenizer, self.processor, text_list)
        return output


i2i = I2I()
index = FaissSearch(config)
index.init_model()

"""
def get_query_idxmap(query_fname):
    print(f"start get qids ")
    query_id = {}
    with open(query_fname, 'r') as fp:
        for line in  fp:
            try:
                qid, query = line.strip().split('\t')
            except:
                continue
            query = query.strip()
            if not query:
                continue
            query_id[qid] = query
    print(f"get query num: {len(query_id)}")
    return query_id

idx2query = get_query_idxmap("../data/query_id")
"""

def gen_output(text_list, func):
    s = time.time()
    if func in "ner":
        output = ner.predict(text_list)
    elif func == "ner_re":
        entity_list = ner.predict(text_list)
        output = re.predict(entity_list)
    e = time.time()
    return output, (e-s)*1000

def get_online_ft_response(query, size):
    body = {"query": query, "ignore_vec": 0, "res_num":size, "type": 2}
    url = "http://10.146.251.212:9800/pagetip_plain_pb?%s" % urlencode(body)
    print(url)
    headers = {}
    payload = {}
    response = requests.request("GET",url,headers=headers, data=payload)
    #print(response.status_code)
    return response.json()

def get_local_ft_response(vecs, size):
    body = {"vectors": [vecs], "res_num":size}
    url = "http://hpcgpu1.ai.lycc.qihoo.net:19000/fasttext/get_by_vectors"
    print("url:", url)
    print("request body:", json.dumps(body))
    headers = {}
    payload = {}
    response = requests.post(url, data=json.dumps(body, ensure_ascii=False))
    print("response:", response)
    print("response.json:", response.json())
    return response.json()

def get_local_ft_reco(query_emb, size):
    try:
        results = get_local_ft_response(query_emb, size)
    except Exception as e:
        raise Exception(repr(e))
    print(results)
    """
    for recos in results['result']:
        for reco in recos["recos"]:
            qid = reco['query_id']
            query = idx2query.get(qid, qid)
            reco['query'] = query
    """
    print(f"get local reco done")
    return results

def get_online_ft_reco(query, size):
    i = 0
    while i<5:
        try:
            results = get_online_ft_response(query, size)
        except Exception as e:
            raise Exception(repr(e))
        if results['result'][0]['vec'] == "":
            time.sleep(0.01)
            i += 1
            continue
        query_emb = results['result'][0]["vec"].strip().split(' ')
        for i in range(len(results['result'])):
            results['result'][i]['vec'] = ""
        break
    if i == 5:
        raise Exception("online fasttext api no result")
    print(f"get online ft reco done")
    return results, query_emb

def get_i2i_embedding(query):
    emb = i2i.predict(query)
    return emb

def get_i2i_topk(query, query_embs, topk):
    results = index.search_with_vecs(query_embs, topk)
    q_predict = results['ids']
    q_dist = results['dist']
    output = []
    for i, query_list in enumerate(zip(q_predict, q_dist)):
        q_l, q_d = query_list
        q_list = zip(q_l, q_d) 
        out = {"query":query[i], "recos":[]}
        for x in q_list:
            out['recos'].append({"query":x[0], "dist":x[1]})
        output.append(out)

    return output

def get_i2i_dist(emb, query):
    dist = index.get_query_dist(emb, query)
    return dist

@app.route('/i2i/dist', methods=['POST', "GET"])
def i2i_dist():
    try:
        args = request.json
        print(f"run compare fastext", args)
        query_a = args.get('query_a', "")
        query_b = args.get('query_b', "")
        emb_a, emb_b = get_i2i_embedding([query_a, query_b])
        dist_ab = get_i2i_dist(emb_a, query_b)
        dist_ba = get_i2i_dist(emb_b, query_a)
        dist = {"query_a": query_a, "query_b":query_b, "dist": {"ab":dist_ab, "ba":dist_ba}}
        out = {"status":0, "message":"success", "data":dist}
        out['request_id'] = args.get('request_id', '')
    except Exception as e:
        print(f"error: {repr(e)}")
        out = {"state": 1, "error_message": repr(e)}
    return out


@app.route('/i2i/topk', methods=['POST', "GET"])
def i2i_topk():
    try:
        args = request.json
        print(f"run compare fastext")
        query = args.get('query', "")
        size = args.get('size', 10)
        query_emb = get_i2i_embedding([query])
        i2i_topk = get_i2i_topk([query], query_emb, size)
        out = {"status":0, "message":"success", "data":i2i_topk, "size": size}
        out['request_id'] = args.get('request_id', '')
    except Exception as e:
        print(f"error: {repr(e)}")
        out = {"state": 1, "error_message": repr(e)}
    return out

@app.route('/fasttext/compare', methods=['POST', "GET"])
def compare_fasttext():
    try:
        args = request.json
        print(f"run compare fastext")
        query = args.get('query', "")
        size = args.get('size', 10)
        online_ft_rt, query_emb = get_online_ft_reco(query, size)
        local_ft_rt = get_local_ft_reco(query_emb, size)
        output = {"online_fasttext": online_ft_rt["result"], "local_fasttext": local_ft_rt["result"]}
        out = {"status":0, "message":"success","query":query, "data":output, "size": size}
        out['request_id'] = args.get('request_id', '')
    except Exception as e:
        print(f"error: {repr(e)}")
        out = {"state": 1, "error_message": repr(e)}
    return out

@app.route('/kg/<name>', methods=['POST'])
def inference(name):
    args = {}
    if request.method == 'POST':
        args = request.json
    print(f"run {name}")
    #print(f"args: {args}")
    text_list = args.get('text', [])
    if name in ["ner", "ner_re"]:
        output, cost = gen_output(text_list, name)
        out = {"status":0, "message":"success", "data":output, "model_cost_ms": cost}
    else:
        out = {"status":1, "message":"unkown function", "data":[], "model_cost_ms": 0}
    out['request_id'] = args.get('request_id', '')
    return out
   
if __name__ == '__main__':
      app.run(debug=False, port=28000, host='0.0.0.0')
