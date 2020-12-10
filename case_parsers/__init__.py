from difflib import SequenceMatcher
import json

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
