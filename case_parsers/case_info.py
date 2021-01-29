import re
import csv
from typing import List, Tuple
import itertools

from . import schema, similar, SEQ_MODEL_AVALIABLE
from case_parsers.seq_match import seq_match, seq_match_multiple

PLAINTIFF_NAME = []


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
    all_casetype = ['民事', '刑事', '行政', '经济', '非诉讼']
    with open('data/formatted/case_type.csv', encoding='UTF-8') as f:
        reader = csv.reader(f,)
        for row in reader:
            matchObj = re.search(r'\d('+row[1]+r')\d', case_id)
            if matchObj is not None:
                for type in all_casetype:
                    if type in row[0]:
                        return type
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
    for element in plaintiff_info:
        PLAINTIFF_NAME.append(element["plaintiff"])
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
                if not stop_searching:
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
    get_plaintiff_info(lines)
    for index, element in enumerate(defendant_info):
        for plaintiff_tmp in PLAINTIFF_NAME:
            if element["defendant"] in plaintiff_tmp or plaintiff_tmp in element["defendant"]:
                defendant_info.pop(index)
                break
            if element["defendant_agent"] in plaintiff_tmp or plaintiff_tmp in element["defendant_agent"]:
                element["defendant_agent"] = 'not found'
            if element["law_firm"] in plaintiff_tmp or plaintiff_tmp in element["law_firm"]:
                element["law_firm"] = 'not found'
        if '保险' in element["defendant"]:
            element["defendant_insurance"] = element["defendant"]
            element["defendant_insurance_agent"] = element["defendant_agent"]
            element["defendant_insurance_lawfirm"] = element["law_firm"]
            del element["defendant"]
            del element["defendant_agent"]
            del element["law_firm"]
    return defendant_info


def get_claims(lines: List[str]) -> Tuple[List[dict], int]:
    basic = '〇一二三四五六七八九'
    claim_num = -1
    start_line_num = 0
    claims: List[dict] = []
    ch_index = None
    for line_num, line in enumerate(lines):
        keyObj = re.search(r'诉称|诉讼请求', line)
        if keyObj is not None:
            start_line_num = line_num
            claim_num = 0
            matchObj = re.search(r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)', line)
            if matchObj is None:
                sentences = line.split('。')
                for sentence in sentences:
                    if keyObj.group() in sentence:
                        matchObj = re.search(r'[:：是](.+)', sentence)
                        if matchObj is not None:
                            claims = [{
                                'con': matchObj.group(1),
                                'line_num': line_num
                            }]
                            return (claims, start_line_num)
        if claim_num >= 0:
            if ch_index is None:
                matchObjs = re.finditer(
                    r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    ch_index = is_ch != -1
                    num = is_ch if ch_index else int(matchObj.group()[0])
                    if num > claim_num:
                        claims.append({
                            'con': matchObj.group(2),
                            'line_num': line_num
                        })
                        claim_num = len(claims)
                    else:
                        return (claims, start_line_num)
            elif ch_index:
                matchObjs = re.finditer(
                    r'[〇一二三四五六七八九][、是](.*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    num = is_ch
                    if num > claim_num:
                        claims.append({
                            'con': matchObj.group(1),
                            'line_num': line_num
                        })
                        claim_num = len(claims)
                    else:
                        return (claims, start_line_num)
            else:
                matchObjs = re.finditer(
                    r'\d[\.、]([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    num = int(matchObj.group()[0])
                    if num > claim_num:
                        claims.append({
                            'con': matchObj.group(1),
                            'line_num': line_num
                        })
                        claim_num = len(claims)
                    else:
                        return (claims, start_line_num)
    return (claims, start_line_num)


def get_controversies(lines: List[str]) -> Tuple[List[dict], int]:
    basic = '〇一二三四五六七八九'
    contro_num = -1
    start_line_num = 0
    controversies: List[dict] = []
    ch_index = None
    for line_num, line in enumerate(lines):
        keyObj = re.search(r'争议(的?焦点|为|是|在于)', line)
        if keyObj is not None:
            start_line_num = line_num
            contro_num = 0
            matchObj = re.search(r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)', line)
            if matchObj is None:
                sentences = line.split('。')
                for sentence in sentences:
                    if keyObj.group() in sentence:
                        matchObj = re.search(r'[:：是](.+|\n)', sentence)
                        if matchObj is not None:
                            if(matchObj.group(1) == '\n'):
                                matchObj = re.search(
                                    r'([〇一二三四五六七八九][、是]|\d[\.、])[^\d]', lines[line_num+1])
                                if matchObj is None:
                                    controversies = [{
                                        'con': lines[line_num+1],
                                        'line_num':line_num+1
                                    }]
                                    return (controversies, start_line_num+1)
                            else:
                                controversies = [{
                                    'con': matchObj.group(1),
                                    'line_num': line_num
                                }]
                                return (controversies, start_line_num)
        if contro_num >= 0:
            if ch_index is None:
                matchObjs = re.finditer(
                    r'([〇一二三四五六七八九][、是]|\d[\.、])([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    ch_index = is_ch != -1
                    num = is_ch if ch_index else int(matchObj.group()[0])
                    if num > contro_num:
                        controversies.append({
                            'con': matchObj.group(2),
                            'line_num': line_num
                        })
                        contro_num = len(controversies)
                    else:
                        return (controversies, start_line_num)
            elif ch_index:
                matchObjs = re.finditer(
                    r'[〇一二三四五六七八九][、是](.*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    is_ch = basic.find(matchObj.group()[0])
                    num = is_ch
                    if num > contro_num:
                        controversies.append({
                            'con': matchObj.group(1),
                            'line_num': line_num
                        })
                        contro_num = len(controversies)
                    else:
                        return (controversies, start_line_num)
            else:
                matchObjs = re.finditer(
                    r'\d[\.、]([^\d].*?)[。;；？\?]', line)
                for matchObj in matchObjs:
                    num = int(matchObj.group()[0])
                    if num > contro_num:
                        controversies.append({
                            'con': matchObj.group(1),
                            'line_num': line_num
                        })
                        contro_num = len(controversies)
                    else:
                        return (controversies, start_line_num)
    return (controversies, start_line_num)


def get_case_summary(lines: List[str]) -> List[dict]:
    (controversies, start_line_num) = get_controversies(lines)
    if len(controversies) == 0:
        (controversies, start_line_num) = get_claims(lines)

    case_summary = [{
        "controversy": controversy['con'],
        "judgement": "",
        "cause": [],
        "basis": []
    } for controversy in controversies]
    try:
        if SEQ_MODEL_AVALIABLE:
            instances = [{
                "con_input": item[0],
                "cause_input":item[1]
            }for item in itertools.product([controversy['con'] for controversy in controversies], lines)]
            results = seq_match_multiple(instances)
            if len(results) == 0:
                raise RuntimeError('seq_match no result')
            results_it = iter(results)
            line_scores = [max([{
                'contro_num': contro_num,
                'score': next(results_it)
            } for contro_num in range(len(controversies))], key=lambda item: item['score'])
                for line_num in range(len(lines)) if line_num > start_line_num]
            for line_num, line_score in enumerate(line_scores):
                if line_score['score'] > 0.5:
                    case_summary[line_score['contro_num']]['cause'].append(
                        lines[line_num+start_line_num].strip())
            for _, case in enumerate(case_summary):
                approve = disapprove = 0
                for match_line in case['cause']:
                    appr_match = re.findall(r'予以(支持|认可|采纳)', match_line)
                    disappr_match = re.findall(r'不予?(支持|认可|采纳)', match_line)
                    approve += len(appr_match)
                    disapprove += len(disappr_match)
                    basis_matchs = re.finditer(
                        '《.+?》(第?[〇一二三四五六七八九十百千]+?条、?)*', match_line)
                    for basis_match in basis_matchs:
                        case['basis'].append(basis_match.group())
                case['judgement'] = str(
                    None if approve + disapprove == 0 else round(approve/(approve+disapprove)))
            return case_summary
    except RuntimeError as e:
        print('get_case_summary error:',e)
    contro_num = 0
    approve = disapprove = 0
    last_contro = 0
    basic = '〇一二三四五六七八九'
    for line_num in range(start_line_num+1, len(lines)):
        for i in range(contro_num, len(controversies)):
            matchObj = re.search(
                '第('+basic[i+1]+'|'+str(i+1)+')个争议焦点', lines[line_num])
            if similar(lines[line_num], controversies[i]['con']) > 0.8 or matchObj is not None:
                if i > last_contro:
                    last_contro = i
    for line_num in range(start_line_num+1, len(lines)):  # TODO: 可能在同一行就出现重要内容，需要判断
        for i in range(contro_num, len(controversies)):
            # 根据争议焦点分段
            matchObj = re.search(
                '第('+basic[i+1]+'|'+str(i+1)+')个争议焦点', lines[line_num])
            if similar(lines[line_num], controversies[i]['con']) > 0.8 or matchObj is not None:
                if i > contro_num:
                    case_summary[contro_num]["controversy"] = controversies[contro_num]['con']
                    case_summary[contro_num]['judgement'] = str(None if approve +
                                                                disapprove == 0 else round(approve/(approve+disapprove)))
                    approve = disapprove = 0
                    contro_num = i
        appr_match = re.findall(r'予以(支持|认可|采纳)', lines[line_num])
        disappr_match = re.findall(r'不予?(支持|认可|采纳)', lines[line_num])
        approve += len(appr_match)
        disapprove += len(disappr_match)
        case_summary[contro_num]['cause'].append(lines[line_num].strip())
        basis_matchs = re.finditer(
            '《.+?》(第?[〇一二三四五六七八九十百千]+?条、?)*', lines[line_num])
        for basis_match in basis_matchs:
            case_summary[contro_num]['basis'].append(basis_match.group())
        if contro_num >= last_contro:
            break

    case_summary[contro_num]["controversy"] = controversies[contro_num]['con']
    case_summary[contro_num]['judgement'] = str(None if approve +
                                                disapprove == 0 else round(approve/(approve+disapprove)))
    return case_summary
