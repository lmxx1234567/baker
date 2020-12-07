import json

lines = []
fields = {}

with open('data/raw/case1.txt') as f:
    lines = f.readlines()

with open('data/formatted/parsed_field.jsonc') as f:
    fields = json.load(f)
