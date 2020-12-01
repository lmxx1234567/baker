import re
import csv

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


def get_cause(lines: [str]) -> str:
    with open('data/formatted/causes') as f:
        causes = f.readlines()
        causes = [cause[:-1] for cause in causes]
        for line in lines:
            for cause in causes:
                if cause in line:
                    return cause
        return 'Not found'


def get_trial_procedure(lines: [str]) -> str:
    case_name = get_case_name(lines)
    for trial_procedure in schema['properties']['trial_procedure']['enum']:
        if trial_procedure in case_name:
            return trial_procedure


def get_case_type(lines: [str]) -> str:
    case_id = get_case_id(lines)
    with open('data/formatted/case_type.csv') as f:
        reader = csv.reader(f,)
        for row in reader:
            matchObj = re.search(r'\d('+row[1]+r')\d', case_id)
            if matchObj is not None:
                return row[0]
    return 'Not found'


def get_court(lines: [str]) -> str:
    for line in lines:
        matchObj = re.search(r'(\S{1,10}(自治)?[省州市县区])+.{1,5}法院', line)
        if matchObj is not None:
            return matchObj.group()
    return 'Not found'
