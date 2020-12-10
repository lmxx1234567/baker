import json

lines = []
fields = {}

with open('data/raw/case1.txt', encoding='UTF-8') as f:
    lines = f.readlines()

with open('data/formatted/parsed_field.jsonc', encoding='UTF-8') as f:
    fields = json.load(f)
