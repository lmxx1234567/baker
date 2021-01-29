import json
import case_parsers
from urllib3 import HTTPConnectionPool
from typing import List

failed_times = 0
try:
    pool = HTTPConnectionPool('127.0.0.1', port=8501, maxsize=32)
except Exception as e:
    print('Can not found sequence matching model!', e)
    case_parsers.SEQ_MODEL_AVALIABLE = False


def check_seq_match_model() -> bool:
    print('Checking sequence matching model...')
    try:
        res = pool.request("GET", '/v1/models/seq_match_bert/metadata')
        if res.status == 200:
            print('ok!')
            return True
        else:
            print('HTTP status code not 200 is', res.status)
            return False
    except Exception as e:
        print('Can not found sequence matching model!', e)
        case_parsers.SEQ_MODEL_AVALIABLE = False
        return False


def seq_match(con: str, cause: str) -> float:
    try:
        data = json.dumps({
            "inputs": {
                "con_input": con,
                "cause_input": cause
            }
        }).encode('utf-8')
        headers = {"Content-Type": "application/json"}
        res = pool.request(
            "POST", '/v1/models/seq_match_bert:predict', headers=headers, body=data)
        res_json = json.loads(res.data.decode('utf-8'))
        return res_json['outputs'][0][0]
    except Exception as e:
        global failed_times
        failed_times += 1
        print('seq_match error:', e)
        if failed_times > 3:
            case_parsers.SEQ_MODEL_AVALIABLE = False
        return -1


def seq_match_multiple(instances: List[dict]) -> List[float]:
    try:
        data = json.dumps({
            "instances": instances
        })
        headers = {"Content-Type": "application/json"}
        res = pool.request(
            "POST", '/v1/models/seq_match_bert:predict', headers=headers, body=data)
        res_json = json.loads(res.data.decode('utf-8'))
        return [item[0]for item in res_json['predictions']]
    except Exception as e:
        global failed_times
        failed_times += 1
        print('seq_match error:', e)
        if failed_times > 3:
            case_parsers.SEQ_MODEL_AVALIABLE = False
        return []
