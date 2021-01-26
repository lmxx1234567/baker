import http
import json
from http import client
import case_parsers

failed_times = 0

def check_seq_match_model() -> bool:
    print('Checking sequence matching model...')
    try:
        conn = client.HTTPConnection('127.0.0.1', 8501, timeout=1)
        conn.request("GET", '/v1/models/seq_match_bert/metadata')
        res = conn.getresponse()
        if res.status == 200:
            print('ok!')
            return True
        else:
            print('HTTP status code not 200 is', res.status)
            return False
    except Exception as e:
        print('Can not found sequence matching model!', e)
        return False


def seq_match(con: str, cause: str) -> float:
    try:
        conn = http.client.HTTPConnection('127.0.0.1', 8501, timeout=1)
        data = json.dumps({
            "inputs": {
                "con_input": con,
                "cause_input": cause
            }
        })
        headers = {"Content-Type": "application/json"}
        conn.request(
            "POST", '/v1/models/seq_match_bert:predict', data, headers)
        res = conn.getresponse()
        res_json = json.load(res)
        return res_json['outputs'][0][0]
    except Exception as e:
        failed_times += 1
        print('seq_match error:', e)
        if failed_times > 10:
            case_parsers.SEQ_MODEL_AVALIABLE = False
        return -1
