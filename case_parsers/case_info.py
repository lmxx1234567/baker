from . import schema
import re


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
