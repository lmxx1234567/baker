import re

from . import schema


def get_case_name(lines: [str]) -> str:
    for line in lines:
        for trial_procedure in schema['properties']['trial_procedure']['enum']:
            if trial_procedure in line:
                return line
    return 'Not found'


def get_case_id(lines: [str]) -> str:
    for line in lines:
        matchObj = re.search(r'[（|()]\d{4}[）|)].+号', line)
        if matchObj is not None:
            return matchObj.group()
    return 'Not found'


def get_year(lines: [str]) -> str:
    case_id = get_case_id(lines)
    matchObj = re.match(r'[（|(](\d{4})[）|)]', case_id)
    if matchObj is not None:
        return matchObj.group(1)
    return 'Not found'
