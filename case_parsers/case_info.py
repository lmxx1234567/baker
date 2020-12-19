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
    with open('data/formatted/causes', encoding='UTF-8') as f:
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
    with open('data/formatted/case_type.csv', encoding='UTF-8') as f:
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


def get_plaintiff_info(lines: List[str]) -> List[dict]:
    import jieba
    import jieba.posseg as pseg
    jieba.enable_paddle()

    find = False
    plaintiff_info = []
    for line in lines:
        if '委托诉讼代理人' in line:
            line = re.sub(r'委托诉讼代理人[：:，,]', '', line)
            seg_list = pseg.cut(line, use_paddle=True)
            plaintiff_agent = law_firm = ''
            for seg in seg_list:
                if seg.flag == 'PER' or seg.flag == 'nr':
                    plaintiff_agent = re.sub(r'[，：；。]', '', seg.word)
                    break
            for seg in seg_list:
                if seg.flag == 'ORG':
                    law_firm = re.sub(r'[，：；。]', '', seg.word)
                    break
            for pinfo in plaintiff_info:
                if pinfo['plaintiff_agent'] == '':
                    pinfo['plaintiff_agent'] = plaintiff_agent
                if pinfo['law_firm'] == '':
                    pinfo['law_firm'] = law_firm
        # Have a name, choose the name first; Otherwise select organization
        elif '原告' in line:
            find = True
            break_it = 0
            line = re.sub(r'原告[：:，,]', '', line)
            seg_list = list(pseg.cut(line, use_paddle=True))
            for seg in seg_list:
                if seg.flag == 'PER' or seg.flag == 'nr':
                    plaintiff_info.append({
                        "plaintiff": re.sub(r'[，：；。]', '', seg.word),
                        "plaintiff_agent": "",
                        "law_firm": ""
                    })
                    break_it = 1
                    break
            if break_it:
                continue
            for seg in seg_list:
                if break_it == 0 and seg.flag == 'ORG':
                    plaintiff_info.append({
                        "plaintiff": re.sub(r'[，：；。]', '', seg.word),
                        "plaintiff_agent": "",
                        "law_firm": ""
                    })
                    break_it = 1
                    break
            if break_it:
                continue
            for seg in seg_list:
                if break_it == 0 and seg.flag == 'nr':
                    plaintiff_info.append({
                        "plaintiff": re.sub(r'[，：；。]', '', seg.word),
                        "plaintiff_agent": "",
                        "law_firm": ""
                    })
                    break_it = 1
                    break
        else:
            if find:
                break
    return plaintiff_info


def get_defendant_info(lines: List[str]) -> List[dict]:
    import jieba
    import jieba.posseg as pseg
    jieba.enable_paddle()

    find = False
    defendant_info = []
    not_found = 0
    stop_searching = False
    for line in lines:
        if stop_searching:
            break
        if similar(line, '委托诉讼代理人') > 0.5:
            line = re.sub(r'委托诉讼代理人[：:，,]', '', line)
            seg_list = pseg.cut(line, use_paddle=True)
            defendant_agent = law_firm = ''
            for seg in seg_list:
                if seg.flag == 'PER' or seg.flag == 'nr':
                    defendant_agent = re.sub(r'[，：；。]', '', seg.word)
                    break
            for seg in seg_list:
                if seg.flag == 'ORG':
                    law_firm = re.sub(r'[，：；。]', '', seg.word)
                    break
            for pinfo in defendant_info:
                if pinfo['defendant_agent'] == '':
                    pinfo['defendant_agent'] = defendant_agent
                if pinfo['law_firm'] == '':
                    pinfo['law_firm'] = law_firm
        elif '被告' in line:
            find = True
            skip_it = False
            defendant_value = None
            line = re.sub(r'被告[：:，,]', '', line)
            seg_list = list(pseg.cut(line, use_paddle=True))
            for seg in seg_list:
                if seg.flag == 'PER':
                    defendant_value = re.sub(r'[，：；。]', '', seg.word)
                    skip_it = True
                    break
            if not skip_it:
                for seg in seg_list:
                    if not skip_it and seg.flag == 'ORG':
                        defendant_value = re.sub(r'[，：；。]', '', seg.word)
                        skip_it = True
                        break
            if not skip_it:
                for seg in seg_list:
                    if not skip_it and seg.flag == 'nr':
                        defendant_value = re.sub(r'[，：；。]', '', seg.word)
                        break
            if defendant_value is not None:
                for info in defendant_info:
                    if defendant_value == info['defendant']:
                        stop_searching = True
                        break
                if not stop_searching :
                    defendant_info.append({
                        "defendant": defendant_value,
                        "defendant_agent": "",
                        "law_firm": ""
                    })
                    defendant_value = None
        else:
            if find:
                if not_found > 1:
                    break
                else:
                    not_found += 1
    return defendant_info


def get_claims(lines: List[str]) -> List[str]:
    basic = '〇一二三四五六七八九'
    claim_num = -1
    claims: List[str] = []
    ch_index = None
    for line in lines:
        if '诉讼请求' in line:
            claim_num = 0
            matchObj = re.search(r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)', line)
            if matchObj is None:
                sentences = line.split('。')
                for sentence in sentences:
                    if '诉讼请求' in sentence:
                        matchObj = re.search(r'[:：](.+)', sentence)
                        if matchObj is not None:
                            claims = [matchObj.group(1)]
                            return claims
        if claim_num >= 0:
            if ch_index is None:
                matchObjs = re.finditer(
                    r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    ch_index = is_ch != -1
                    num = is_ch if ch_index else int(matchObj.group()[0])
                    if num > claim_num:
                        claims.append(matchObj.group(2))
                        claim_num = len(claims)
                    else:
                        return claims
            elif ch_index:
                matchObjs = re.finditer(
                    r'[〇一二三四五六七八九][、是](.*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    num = is_ch
                    if num > claim_num:
                        claims.append(matchObj.group(1))
                        claim_num = len(claims)
                    else:
                        return claims
            else:
                matchObjs = re.finditer(
                    r'\d[\.、]([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    num = is_ch
                    if num > claim_num:
                        claims.append(matchObj.group(1))
                        claim_num = len(claims)
                    else:
                        return claims
    return claims


def get_controversies(lines: List[str]) -> List[str]:
    basic = '〇一二三四五六七八九'
    contro_num = -1
    controversies: List[str] = []
    ch_index = None
    for line in lines:
        keyObj = re.search(r'争议(的?焦点|为|是|在于)', line)
        if keyObj is not None:
            contro_num = 0
            matchObj = re.search(r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)', line)
            if matchObj is None:
                sentences = line.split('。')
                for sentence in sentences:
                    if keyObj.group() in sentence:
                        matchObj = re.search(r'[:：](.+)', sentence)
                        if matchObj is not None:
                            controversies = [matchObj.group(1)]
                            return controversies
        if contro_num >= 0:
            if ch_index is None:
                matchObjs = re.finditer(
                    r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    ch_index = is_ch != -1
                    num = is_ch if ch_index else int(matchObj.group()[0])
                    if num > contro_num:
                        controversies.append(matchObj.group(2))
                        contro_num = len(controversies)
                    else:
                        return controversies
            elif ch_index:
                matchObjs = re.finditer(
                    r'[〇一二三四五六七八九][、是](.*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    num = is_ch
                    if num > contro_num:
                        controversies.append(matchObj.group(1))
                        contro_num = len(controversies)
                    else:
                        return controversies
            else:
                matchObjs = re.finditer(
                    r'\d[\.、]([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    num = is_ch
                    if num > contro_num:
                        controversies.append(matchObj.group(1))
                        contro_num = len(controversies)
                    else:
                        return controversies
    return controversies


def get_case_summary(lines: List[str]) -> List[dict]:
    controversies = get_controversies(lines)
    start_line_num = 0
    if len(controversies) > 0:
        for line_num, line in enumerate(lines):
            keyObj = re.search(r'争议(的?焦点|为|是|在于)', line)
            if keyObj is not None:
                start_line_num = line_num
    else:
        controversies = get_claims(lines)
        for line_num, line in enumerate(lines):
            if '诉讼请求' in line:
                start_line_num = line_num

    contro_num = 0
    case_summary = [{
        "controversy": controversy,
        "judgement": "",
        "cause": [],
        "basis": []
    } for controversy in controversies]
    approve = disapprove = 0
    last_contro = 0
    for line_num in range(start_line_num+1, len(lines)):
        for i in range(contro_num, len(controversies)):
            if similar(lines[line_num], controversies[i]) > 0.8:
                last_contro = i
    for line_num in range(start_line_num+1, len(lines)):  # TODO: 可能在同一行就出现重要内容，需要判断
        for i in range(contro_num, len(controversies)):
            if similar(lines[line_num], controversies[i]) > 0.8:
                if i > contro_num:
                    case_summary[contro_num]["controversy"] = controversies[contro_num]
                    case_summary[contro_num]['judgement'] = str(None if approve +
                                                                disapprove == 0 else round(approve/(approve+disapprove)))
                    approve = disapprove = 0
                    contro_num = i
        appr_match = re.findall(r'予以(支持|认可)', lines[line_num])
        disappr_match = re.findall(r'不予?(支持|认可)', lines[line_num])
        approve += len(appr_match)
        disapprove += len(disappr_match)
        if contro_num >= last_contro:
            cause_matchs = re.findall(r'本院认为.*[.。;；]', lines[line_num])
            for cause_match in cause_matchs:
                case_summary[contro_num]['cause'].append(cause_match)
        else:
            case_summary[contro_num]['cause'].append(lines[line_num].strip())
        basis_matchs = re.finditer(
            '《.+?》(第?[〇一二三四五六七八九十百千]+?条、?)*', lines[line_num])
        for basis_match in basis_matchs:
            case_summary[contro_num]['basis'].append(basis_match.group())

    case_summary[contro_num]["controversy"] = controversies[contro_num]
    case_summary[contro_num]['judgement'] = str(None if approve +
                                                disapprove == 0 else round(approve/(approve+disapprove)))
    return case_summary
