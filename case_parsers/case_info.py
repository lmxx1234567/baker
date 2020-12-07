import re
import csv
from typing import List

from . import schema, similar


def get_case_name(lines: List[str]) -> str:
    for line in lines:
        line = re.sub(r'　|\s', '', line)
        for trial_procedure in schema['properties']['document_type']['enum']:
            if trial_procedure in line:
                return line
    return 'Not found'


def get_case_id(lines: List[str]) -> str:
    for line in lines:
        matchObj = re.search(r'[（|()]\d{4}[）|)].+号', line)
        if matchObj is not None:
            return matchObj.group()
    return 'Not found'


def get_year(lines: List[str]) -> str:
    case_id = get_case_id(lines)
    matchObj = re.match(r'[（|(](\d{4})[）|)]', case_id)
    if matchObj is not None:
        return matchObj.group(1)
    return 'Not found'


def get_cause(lines: List[str]) -> str:
    with open('data/formatted/causes') as f:
        causes = f.readlines()
        causes = [cause[:-1] for cause in causes]
        for line in lines:
            for cause in causes:
                if cause in line:
                    return cause
        return 'Not found'


def get_trial_procedure(lines: List[str]) -> str:
    case_name = get_case_name(lines)
    for trial_procedure in schema['properties']['trial_procedure']['enum']:
        if trial_procedure in case_name:
            return trial_procedure


def get_case_type(lines: List[str]) -> str:
    case_id = get_case_id(lines)
    with open('data/formatted/case_type.csv') as f:
        reader = csv.reader(f,)
        for row in reader:
            matchObj = re.search(r'\d('+row[1]+r')\d', case_id)
            if matchObj is not None:
                return row[0]
    return 'Not found'


def get_court(lines: List[str]) -> str:
    for line in lines:
        matchObj = re.search(r'(\S{1,10}(自治)?[省州市县区])+.{1,6}法院', line)
        if matchObj is not None:
            return matchObj.group()
    return 'Not found'


def get_document_type(lines: List[str]) -> str:
    for line in lines:
        for dtype in schema['properties']['document_type']['enum']:
            if dtype in line:
                return dtype
    return 'Not found'


def get_judge(lines: List[str]) -> str:
    for line in reversed(lines):
        line = re.sub(r'　|\s', '', line)
        if '审判员' in line:
            return re.sub(r'(审判员)|[　\s]+', '', line)
    return 'Not found'


def get_clerk(lines: List[str]) -> str:
    for line in reversed(lines):
        line = re.sub(r'　|\s', '', line)
        if '书记员' in line:
            return re.sub(r'(书记员)|[　\s]+', '', line)
    return 'Not found'


def get_case_summary(lines: List[str]) -> List[dict]:
    basic = '〇一二三四五六七八九'
    contro_num = -1
    controversies: List[str] = []
    start_line_num = 0
    for line_num in range(len(lines)):
        flag = False
        if '争议焦点' in lines[line_num]:
            contro_num = 0
            start_line_num = line_num
        if contro_num >= 0:
            matchObjs = re.finditer(
                r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)[.。;；]', lines[line_num])
            for matchObj in matchObjs:
                is_ch = basic.find(matchObj.group()[0])
                num = is_ch if is_ch != -1 else int(matchObj.group()[0])
                if num > contro_num:
                    controversies.append(matchObj.group(2))
                    contro_num = len(controversies)
                else:
                    flag = True
                    break
        if flag:
            break

    contro_num = 0
    case_summary = [{
        "controversy": controversy,
        "judgement": "",
        "cause": "",
        "basis": ""
    } for controversy in controversies]
    approve = disapprove = 0
    for line_num in range(start_line_num+1, len(lines)):
        for i in range(contro_num, len(controversies)):
            if similar(lines[line_num], controversies[i]) > 0.8:
                if i > contro_num:
                    case_summary[contro_num]["controversy"] = controversies[contro_num]
                    case_summary[contro_num]['judgement'] = None if approve + \
                        disapprove == 0 else approve/(approve+disapprove)
                    approve = disapprove = 0
                    contro_num = i
        appr_match = re.findall(r'予以(支持)|(认可)', lines[line_num])
        disappr_match = re.findall(r'不予?(支持)|(认可)', lines[line_num])
        approve += len(appr_match)
        approve += len(disappr_match)
        cause_matchs = re.findall(r'本院认为.*[.。;；]', lines[line_num])
        for cause_match in cause_matchs:
            case_summary[contro_num]['cause'] += cause_match
        basis_matchs = re.finditer(
            '《.+?》(第?[〇一二三四五六七八九十百千]+?条、?)*', lines[line_num])
        for basis_match in basis_matchs:
            case_summary[contro_num]['basis'] += basis_match.group()

    case_summary[contro_num]["controversy"] = controversies[contro_num]
    case_summary[contro_num]['judgement'] = None if approve + \
        disapprove == 0 else approve/(approve+disapprove)
    return case_summary
