from difflib import SequenceMatcher
import json
from case_parsers import sequence_match,controversy_mark

schema = {}

with open('data/formatted/parsed_field_schema.jsonc', encoding='UTF-8') as f:
    schema = json.load(f)


def similar(string: str, sub: str) -> float:
    sm = SequenceMatcher(None, string, sub)
    matchs = sm.get_matching_blocks()
    size = 0
    for match in matchs:
        size += match.size
    return size/len(sub)

SEQ_MODEL_AVALIABLE = sequence_match.check_seq_match_model()
CON_MARK_MODEL_AVALIABLE = controversy_mark.check_con_mark_model()

from case_parsers.case_info import * 
from case_parsers.case_info_v2 import *
