import json

lines = []
with open('case.txt') as f:
    lines = f.readlines()


def loadField(fields):
    if type(fields) == dict:
        for key, value in fields.items():
            fields[key] = loadField(value)
        return fields
    elif type(fields) == list:
        for index, value in enumerate(fields):
            fields[index] = loadField(value)
        return fields
    elif type(fields) == str and fields != '':
        for lineNum, line in enumerate(lines):
            index = line.find(fields)
            if index != -1:
                return {
                    "content": fields,
                    "line": lineNum,
                    "start": index,
                    "stop": lineNum+len(fields)
                }
        return fields
    else:
        return fields


with open('parsed_field.json') as f:
    fields = json.load(f)
    loadField(fields)

    print(json.dumps(fields, ensure_ascii=False))
