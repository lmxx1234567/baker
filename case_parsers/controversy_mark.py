import json
import case_parsers
from urllib3 import HTTPConnectionPool
from typing import List
import numpy as np

failed_times = 0
try:
    pool = HTTPConnectionPool('127.0.0.1', port=8502, maxsize=32)
except Exception as e:
    print('Can not found controversy marking model!', e)
    case_parsers.CON_MARK_MODEL_AVALIABLE = False


def check_con_mark_model() -> bool:
    print('Checking controversy marking model...')
    try:
        res = pool.request("GET", '/v1/models/con_mark/metadata')
        if res.status == 200:
            print('ok!')
            return True
        else:
            print('HTTP status code not 200 is', res.status)
            return False
    except Exception as e:
        print('Can not found controversy marking model!', e)
        case_parsers.CON_MARK_MODEL_AVALIABLE = False
        return False


def con_mark(text: str) -> List[str]:
    try:
        data = json.dumps({
            "inputs": text
        }).encode('utf-8')
        headers = {"Content-Type": "application/json"}
        res = pool.request(
            "POST", '/v1/models/con_mark:predict', headers=headers, body=data)
        res_json = json.loads(res.data.decode('utf-8'))
        predictions = res_json['outputs'][0]
        return predictions2str(text, predictions)
    except Exception as e:
        global failed_times
        failed_times += 1
        print('con_mark error:', e)
        if failed_times > 3:
            case_parsers.CON_MARK_MODEL_AVALIABLE = False
        return ''


def con_mark_multiple(instances: List[str]) -> List[List[str]]:
    try:
        data = json.dumps({
            "instances": instances
        })
        headers = {"Content-Type": "application/json"}
        res = pool.request(
            "POST", '/v1/models/con_mark:predict', headers=headers, body=data)
        res_json = json.loads(res.data.decode('utf-8'))
        return [predictions2str(instances[i], item)for i, item in enumerate(res_json['predictions'])]
    except Exception as e:
        global failed_times
        failed_times += 1
        print('con_mark error:', e)
        if failed_times > 3:
            case_parsers.CON_MARK_MODEL_AVALIABLE = False
        return []


def predictions2str(text: str, predictions: List[List[float]]) -> List[str]:
    predictions = np.argsort(predictions)
    text_list = []
    text_generated = ''
    predict = 0
    for i, predict_idxs in enumerate(predictions):
        if predict in [0, 3]:
            for idx in predict_idxs:
                if idx in [0, 1]:
                    predict = idx
        elif predict in [1, 2]:
            for idx in predict_idxs:
                if idx in [2, 3]:
                    predict = idx
        if predict == 1:
            if i < len(text):
                tmp_text = ''
                tmp_text += text[i]
            else:
                break
        elif predict == 2:
            if i < len(text):
                tmp_text += text[i]
            else:
                break
        elif predict == 3:
            if i < len(text):
                tmp_text += text[i]
                if len(tmp_text) < 5:
                    text_generated += tmp_text
                else:
                    if text_generated != '':
                        text_list.append(text_generated)
                    text_list.append(tmp_text)
                    text_generated = ''
            else:
                break
    return text_list
