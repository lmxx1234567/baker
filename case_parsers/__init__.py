import json

schema={}

with open('data/formatted/parsed_field_schema.jsonc') as f:
    schema = json.load(f)