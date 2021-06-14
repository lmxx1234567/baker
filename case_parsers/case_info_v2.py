# 'filing_date','judgment_date','discharge_date','city_class','hospital','diagnosis','previous'，
# 事故日期：accident_date
# 评残日期：disable_assessment_date
# 正则标准：年份必须是四位数，否则标准化时将出问题，年和月无所谓（XXXX年XX月XX日，XXXX/XX/XX, XXXX\XX\XX,XXXX年XX月XX号）
import datetime
import re
from typing import Dict, List

from case_parsers import case_info

pattern = re.compile(
    '\d{2,4}[\.\-/年]{1}\d{1,2}[\.\-/月]{1}\d{1,2}[日号]{0,1}|[一二].{1,3}年.{1,2}月.{1,3}[日号]{1}')
pattern_ym = re.compile(
    '\d{2,4}[\.\-/年]{1}\d{1,2}[\.\-/月]|[一二].{1,3}年.{1,2}月')
pattern_year = re.compile(
    '\d{2,4}[\.\-/年]|[一二].{1,3}年')
pattern_accdate = re.compile(
    '[2].\d{1,3}[\.\-/年]{1}\d{1,2}[\.\-/月]{1}\d{1,2}[日号]{0,1}|[一二].{1,3}年.{1,2}月.{1,3}[日号]{1}')
replace_lists = [{'年': '-', '月': '-', '日': '', '\.': '-', '/': '-', '号': ''},
                 {'九': '9', '八': '8', '七': '7', '六': '6', '五': '5', '四': '4', '三': '3',
                     '二': '2', '一': '1', '元': '1', '○': '0', '〇': '0', '零': '0', 'O': '0'},
                 {'三十一': '31', '三十': '30', '二十九': '29', '二十八': '28', '二十七': '27', '二十六': '26', '二十五': '25', '二十四': '24', '二十三': '23', '二十二': '22', '二十一': '21', '二十': '20', '十九': '19', '十八': '18', '十七': '17', '十六': '16', '十五': '15', '十四': '14', '十三': '13', '十二': '12', '十一': '11', '十': '10', '九': '09', '八': '08', '七': '07', '六': '06', '五': '05', '四': '04', '三': '03', '二': '02', '一': '01', '元': '01'}]
pattern2 = re.compile(
    '[一二].{1,3}年.{1,2}月.{1,3}[日号]{1}')
capital_num = r'九|八|七|六|五|四|三|二|一|元|○|〇|零|\d'
capital_kuohao = r'（[九八七六五四三二一元○〇零\d]）'


def date_format(raw_date: str) -> str:
    for key, value in replace_lists[0].items():
        raw_date = re.sub(key, value, raw_date)
    yearlen = len((raw_date.split('-'))[0])
    year = raw_date[0:yearlen]
    mon_day = raw_date[yearlen:]
    for key, value in replace_lists[1].items():
        year = re.sub(key, value, year)
    for key, value in replace_lists[2].items():
        mon_day = re.sub(key, value, mon_day)
    format_date = year+mon_day
    tmp = format_date.split('-')
    try:
        format_date = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2])).strftime(
            "%{0}-%m-%d".format('Y' if yearlen == 4 else 'y'))
    except ValueError as e:
        return raw_date
    return format_date

# trial_date审理日期:‘审理’关键字段落寻找日期


def get_trial_date(lines: List[str]) -> str:
    trial_date = None
    for line in lines:
        if line == '\n':
            continue
        if re.search(r'审理|开庭', line) is not None:
            line = re.sub(r'\s', '', line)
            line = re.split(r'[，：；。]', line)
            for subline in line:
                if "审理" in subline:
                    trial_date = pattern.search(subline)
                if trial_date is None and "同年" in subline:
                    tmpyear = get_accident_date(lines)
                    if tmpyear is not None:
                        tmpyear = tmpyear.split("-")[0]+"年"
                        subline2 = re.sub("同年", tmpyear, subline)
                        trial_date = pattern.search(subline2)
                if trial_date is not None:
                    break
        if trial_date is not None:
            trial_date = date_format(trial_date[0])
            break
    return trial_date

# filing_date立案日期:‘立案’关键字段落寻找日期


def get_filing_date(lines: List[str]) -> str:
    filing_date = None
    for line in lines:
        if line == '\n':
            continue
        if "立案" in line:
            line = re.sub(r'\s', '', line)
            line = re.split(r'[，：；。]', line)
            for subline in line:
                if "立案" in subline:
                    filing_date = pattern.search(subline)
                if filing_date is None and "同年" in subline:
                    tmpyear = get_accident_date(lines)
                    if tmpyear is not None:
                        tmpyear = tmpyear.split("-")[0]+"年"
                        subline2 = re.sub("同年", tmpyear, subline)
                        filing_date = pattern.search(subline2)
                if filing_date is not None:
                    break
        if filing_date is not None:
            filing_date = date_format(filing_date[0])
            break
        else:
            if "受理" in line:
                line = re.sub(r'\s', '', line)
                line = re.split(r'[，：；。]', line)
                for subline in line:
                    if "受理" in subline:
                        filing_date = pattern.search(subline)
                    if filing_date is not None:
                        break
            if filing_date is not None:
                filing_date = date_format(filing_date[0])
                break
    return filing_date

# 文末判决日期


def get_judgment_date(lines: List[str]) -> str:
    for line in reversed(lines):
        line = re.sub(r'\s', '', line)
        judgment_date = pattern2.search(line)
        if judgment_date is not None:
            judgment_date = date_format(judgment_date[0])
            break
    return judgment_date

# 出院日期:于...出院;...出院
# 若出现同年，则与事故日期保持一致


def get_discharge_date(lines: List[str]) -> str:
    discharge_date = None
    for line in lines:
        if line == '\n':
            continue
        if "出院" in line:
            line = re.sub(r'\s', '', line)
            line = re.split(r'[，：；。]', line)
            for subline in line:
                if "出院" in subline:
                    discharge_date = pattern.search(subline)
                    if discharge_date is None and "同年" in subline:
                        tmpyear = get_accident_date(lines)
                        if tmpyear is not None:
                            tmpyear = tmpyear.split("-")[0]+"年"
                            subline2 = re.sub("同年", tmpyear, subline)
                            discharge_date = pattern.search(subline2)
                if discharge_date is not None:
                    break
        if discharge_date is not None:
            discharge_date = date_format(discharge_date[0])
            break
    return discharge_date

# 从前往后找到的第一个法院名字


def get_city_class(lines: List[str]) -> Dict:
    import cpca
    import jieba
    import jieba.posseg as pseg
    jieba.enable_paddle()
    court_name = None
    citylist = []
    for line in lines:  # 提取人民法院名称
        if line == '\n':
            continue
        line = re.sub(r'\s+', '', line)
        if "人民法院" in line:
            line = re.split(r'[，：；。\s+]', line)
            for subline in line:
                if "人民法院" in subline:
                    subline = re.sub(r'[\n\s]', '', subline)
                    seg_list = pseg.cut(subline, use_paddle=True)
                    for seg in seg_list:
                        if seg.flag == 'ns' or seg.flag == 'nt' or seg.flag == 'ORG':
                            court_name = re.sub(r'[，：；。]', '', seg.word)
                            break
                if court_name is not None:
                    break
        if court_name is not None:  # 进行地市分级
            city = re.sub(r'(中级|最高)?人民法院', '', court_name)
            citylist.append(city)
            city_class = cpca.transform(citylist)
            city_class_form = city_class.iloc[0].to_dict()
            for (key, value) in city_class_form.items():
                if city_class_form[key] is not None:
                    return city_class.iloc[0].to_dict()
            court_name = None
            citylist = []
    return city_class.iloc[0].to_dict()


def get_hospital(lines: List[str]) -> List[str]:
    import jieba
    import jieba.posseg as pseg
    jieba.enable_paddle()
    treatment = None
    transfer = None
    treatment_hospital = []
    transfer_hospital = []
    for line in lines:
        if line == '\n':
            continue
        if re.search(r'医院|卫生院', line) is not None:
            line = re.sub(r'[\n\s]', '', line)
            line = re.split(r'[，：；＋。、.《》]', line)
            for subline in line:
                if re.search(r'医院|卫生院', subline) is not None:
                    seg_list = pseg.cut(subline, use_paddle=True)
                    for seg in seg_list:
                        if (seg.flag == 'ns' or seg.flag == 'nt' or seg.flag == 'ORG') and (re.search(r'医院|卫生院', seg.word) is not None):
                            if "转" in subline:
                                transfer = (re.split(r'医院|卫生院', seg.word))[
                                    0]+re.search(r'医院|卫生院', seg.word)[0]
                                if re.search(r'（|经|至|\d{1}\.', transfer[0]) is not None:
                                    transfer = transfer[1:]
                                if bool([True for h_info in transfer_hospital if transfer in h_info]):
                                    continue
                                transfer_hospital.append(transfer)
                            else:
                                treatment = (re.split(r'医院|卫生院', seg.word))[
                                    0]+re.search(r'医院|卫生院', seg.word)[0]
                                if re.search(r'（|经|至|\d{1}\.|）', treatment[0:3]) is not None:
                                    # treatments = re.split(r'（|经|至|(\d{1}\.)',treatment)
                                    # if len(treatments)<2:
                                    #     treatment=treatments[1]
                                    # else:
                                    treatment = re.sub(
                                        capital_kuohao, '', treatment)
                                    treatment = re.sub(
                                        r'（|经|至|\d\.|）', '', treatment)
                                if bool([True for h_info in treatment_hospital if treatment in h_info]) or re.search(r'受伤|送', treatment) is not None:
                                    continue
                                if re.search(r'（', treatment) is not None and re.search(r'）', treatment) is None:
                                    continue
                                if re.search(r'（', treatment) is None and re.search(r'）', treatment) is not None:
                                    continue
                                # if treatment in all_hos_list:
                                #     treatment_hospital.append(treatment)
                                # elif re.search(r'第|市|县|区|人民', treatment) is not None:
                                #     treatment_hospital.append(treatment)
                                # elif re.search(capital_num, treatment) is not None:
                                treatment_hospital.append(treatment)
    if transfer_hospital:
        transfer_hospital = list(set(transfer_hospital))
        return transfer_hospital
    if treatment_hospital:
        treatment_hospital = list(set(treatment_hospital))
        return treatment_hospital
    return treatment_hospital.append("None")


# 诊断规则：诊断开始截取，到‘等’或句号结束。所有诊断截取的存为list，比较相似性，相似性接近时，取长的；--目前没有比较相似性
# 有多个诊断时，排除‘诊断书’‘诊断证明’所在的list,留下'诊断'被判断为动词的list
def get_diagnosis(lines: List[str]) -> List[str]:
    # import jieba
    # import jieba.posseg as pseg
    # jieba.enable_paddle()
    tmp_diagnosis = []
    accept = {}
    diagnosis = []
    # 存储所有带有“诊断”的list
    for line in lines:
        if line == '\n':
            continue
        if "诊断" in line:
            line = re.sub(r'\s', '', line)
            line = re.split(r'[。 ！]', line)
            for period_subline in line:
                if "诊断" in period_subline:
                    half = re.split("诊断", period_subline)
                    period_subline = re.split(r'[，：；]', period_subline)
                    for comma_index, comma_subline in enumerate(period_subline):
                        if "诊断" in comma_subline:
                            diag = (re.split("诊断", comma_subline))[
                                0]+"诊断"+half[1]
                            tmp_diagnosis.append(diag)
                            # break
                    # break
    # 排除诊断书、诊断说明
    for num, diag in enumerate(tmp_diagnosis):
        accept[num] = False
        diag0 = re.sub("诊断证?[书明]", "", diag)
        if "诊断" in diag0:
            if diag0[-3:]!="：主要":
                accept[num] = True
    for (key, value) in accept.items():
        if accept[key] == True:
            diagnosis.append(tmp_diagnosis[key])
    return diagnosis

# previous:既往上下文提取
# 说明：从‘既往’关键字出现的短句（即逗号、分号拆分结果）开始截取，到句号或分号结束:
# 到分号结束：无其他规则；
# 到句号结束：判断短句中是否出现关键字‘既往’、‘病’、‘院’、‘就诊’、‘科室’中任意字样，如有，则继续，否则截取结束。


def get_previous(lines: List[str]) -> List[str]:
    previous = ''
    keywords = ["既往", "病", "院", "就诊", "科室"]
    starthere = False
    takeit = False
    for line in lines:
        if line == '\n':
            continue
        # 请保留此注释，目前标注样例少，下面的注释部分可能用于后续优化
        # if "既往" in line:
        #     line = re.split(r'[； ！]', line)
        #     for period_subline in line:
        #         if "既往" in period_subline:
        #             half = re.split("既往", period_subline)
        #             period_subline = re.split(r'[，：；]', period_subline)
        #             for comma_index, comma_subline in enumerate(period_subline):
        #                 if "既往" in comma_subline:
        #                     prev = (re.split("既往", comma_subline))[0]+"既往"+half[1]
        #                     previous.append(prev)
        #                     break
        #             break
        line = line.split('。')
        for period_subline in line:
            if "既往" in period_subline:
                period_subline = re.sub(r'\s', '', period_subline)
                period_subline = re.findall(
                    '.*?[：；]', period_subline)  # 更精细的时候要加上逗号
                for comma_subline in period_subline:
                    if "既往" in comma_subline:
                        starthere = True
                    if starthere is True:
                        takeit = False
                        for keyword in keywords:
                            if keyword in comma_subline:
                                takeit = True
                                previous += comma_subline
                                break
                    if starthere is True and takeit is False:
                        return previous
    if not previous:
        previous = '无'
    return previous

# 事故日期：accident_date
# 优化思路：目前没有时分秒，优化的时候考虑：有时分秒优先时分秒，否则第一个日期

# TODO: 需要测试


def get_accident_date(lines: List[str]) -> str:
    p_list = [r'(下列)?事实.?(理由)?', '诉称', '辩称', '事故发生概况',
              '诉讼请求', r'经审理(查明)?(认定)?', '本院认定事实如下']
    for p in p_list:
        torline = 0
        accident_date = None
        acc_19 = None
        nextline = False
        for line in lines:
            if line == '\n':
                continue
            if nextline is True:
                torline += 1
                sublines = re.split(r'[，：:；。]', line)
                for subline in sublines:
                    accident_date = pattern_accdate.search(subline)
                    if acc_19 is None:
                        acc_19 = pattern.search(subline)
                    if accident_date is not None:
                        return date_format(accident_date[0])
            if torline > 4 and acc_19 is not None:
                return date_format(acc_19[0])

            keyObj = re.search(p, line)
            if keyObj is not None:
                line_spl = re.split(p, line)
                if line_spl[-1] is not None:
                    line_spl = re.split(r'[，：:；。]', line_spl[-1])
                try:
                    if '\n' in line[1]:
                        nextline = True
                        continue
                except Exception:
                    nextline = True
                    continue
                torline += 1
                for subline in line_spl:
                    if subline is not None:
                        accident_date = pattern_accdate.search(subline)
                        if acc_19 is None:
                            acc_19 = pattern.search(subline)
                        if accident_date is not None:
                            return date_format(accident_date[0])
            if torline > 4 and acc_19 is not None:
                return date_format(acc_19[0])

    return accident_date

# 评残日期：disable_assessment_date


def get_disable_assessment_date(lines: List[str]) -> str:
    disable_assessment = None
    p_list = [r'级.?残', r'伤残.*级', r'鉴定(所|中心).*(出具|[作做]出)', r'鉴定(所|中心)']
    for p in p_list:
        for line in lines:
            if line == '\n':
                continue
            keyObj = re.search(p, line)
            if keyObj is not None:
                line = re.split(r'[；。]', line)
                for subline in line:
                    keyObj = re.search(p, subline)
                    if keyObj is not None:
                        disable_assessment = pattern.search(subline)
                    if disable_assessment is None and "同年" in subline:
                        tmpyear = get_accident_date(lines)
                        if tmpyear is not None:
                            tmpyear = tmpyear.split("-")[0]+"年"
                            subline2 = re.sub("同年", tmpyear, subline)
                            disable_assessment = pattern.search(subline2)
                    if disable_assessment is not None:
                        return date_format(disable_assessment[0])
    return disable_assessment

# 伤者相关：injured
# {injured_name:xx, injured_birth:xx,injured_sex:男女, injured_work:xx,injured_education:xx,injured_resident:xx,injured_marriage:xx}
# 需要排除被告：已完成--data/provide/scase3
# 有人姓名会被识别成组织ORG---case5


def _deldup(lines: List[str], injured_list: List[dict]) -> List[dict]:
    dupname = {}
    tmp_list = injured_list
    restart = False
    breakwhile = False
    maxn = len(injured_list)
    while(1-breakwhile and maxn > 0):
        maxn = maxn-1
        for i, injure1 in enumerate(tmp_list):
            for j, injure2 in enumerate(tmp_list[i+1:]):
                if (injure1["injured_name"] in injure2["injured_name"]) or (injure2["injured_name"] in injure1["injured_name"]):
                    dupname[injure1["injured_name"]] = 0
                    dupname[injure2["injured_name"]] = 0
                    for line in lines:
                        dupname[injure1["injured_name"]
                                ] += len(re.findall(injure1["injured_name"].replace('*', '某'), line))
                        dupname[injure2["injured_name"]
                                ] += len(re.findall(injure2["injured_name"].replace('*', '某'),line))
                    if dupname[injure1["injured_name"]] == dupname[injure1["injured_name"]]:
                        if len(injure1["injured_name"]) >= len(injure2["injured_name"]):
                            tmp_list.pop(j+i+1)
                            restart = True
                        else:
                            tmp_list.pop(i)
                            restart = True
                if restart:
                    break
            if restart:
                restart = False
                break
            if i == len(tmp_list)-1:
                breakwhile = True
    return tmp_list


def _get_injured_name(lines: List[str], plaintiff_info) -> List[dict]:
    import jieba
    import jieba.posseg as pseg
    jieba.enable_paddle()
    injured_list = []
    name = r'(原告)'
    defendant_info = get_defendant_info(lines)
    # get_accident_line
    p_list = [r'受伤', r'(当场)?死亡(?!证明|赔偿|殡葬|医学)']
    # [r'(住(?!院))|生活(?!费|来源)']
    for statue, p in enumerate(p_list):
        for line in lines:
            if line == '\n':
                continue
            if "本院认为" in line:
                break
            keyObj = re.search(p, line)
            if keyObj is not None:
                sublines = re.split(r'[，：:；。]', line)
                for subline in sublines:
                    Mayfind = False
                    keyObj = re.search(p, subline)
                    if keyObj is not None:
                        subline = re.sub(r'[\n\s]', '', subline)
                        subline = re.sub(r'、', '&', subline)
                        seg_list = pseg.cut(subline, use_paddle=True)
                        Mayfind = True
                        for seg in seg_list:
                            is_split = True
                            if seg.flag == 'PER' or seg.flag == 'nr':
                                injuerd = re.sub(r'[，：；。（）]', '', seg.word)
                                try:
                                    injuerd_withnum = (
                                        subline.split(seg.word)[1])[0]
                                except Exception:
                                    is_split = False
                                if is_split:
                                    if re.search(r'[123456789]', injuerd_withnum) is not None:
                                        injuerd = injuerd + injuerd_withnum
                                if len(injuerd) > 3 and re.search(r'导?致', injuerd) is not None:
                                    injuerd = re.sub(r'导?致', '', injuerd)
                                if '原告' in subline and re.search(r'(原告).*[及&和与]', subline) is None and re.search(r'[及&和与].*(原告)', subline) is None:
                                    break
                                injuerd = re.split("&", injuerd)
                                for i in injuerd:
                                    i = re.sub(r'[，：；。（）()]', '', i)
                                    # 如果已经存在则不插入，如果在被告中出现就不插入
                                    if bool([True for i_info in injured_list if i in i_info.values()]) or bool([True for defendant in defendant_info if i in defendant.values()]):
                                        continue
                                    if re.search(r'晋A', i):
                                        continue
                                    injured_info = {'injured_name': '', 'injured_birth': 'null', 'injured_sex': 'null',
                                                    'injured_work': 'null', 'injured_education': 'null', 'injured_resident': 'null', 'injured_marriage': []}
                                    injured_info['injured_name'] = i
                                    injured_list.append(injured_info)
                        if statue == 0:
                            # 造成原告受伤，没提姓名----provide/case6
                            keyObj_name = re.search(name, subline)
                            if Mayfind and keyObj_name is not None:
                                for plaint in plaintiff_info:
                                    injuerd = plaint["plaintiff"]
                                    if bool([True for injured_info in injured_list if injuerd in injured_info.values()]):
                                        continue
                                    injured_info = {'injured_name': '', 'injured_birth': 'null', 'injured_sex': 'null',
                                                    'injured_work': 'null', 'injured_education': 'null', 'injured_resident': 'null', 'injured_marriage': []}
                                    injured_info['injured_name'] = injuerd
                                    injured_list.append(injured_info)
                    subline = re.sub(r'&', '、', subline)
    if len(injured_list) > 1:
        _deldup(lines, injured_list)
    # 如果伤者为空，就把原告放进去
    if len(injured_list) == 0:
        for plaint in plaintiff_info:
            injuerd = plaint["plaintiff"]
            if bool([True for injured_info in injured_list if injuerd in injured_info.values()]):
                continue
            if plaint["is_company"]:
                continue
            injured_info = {'injured_name': '', 'injured_birth': 'null', 'injured_sex': 'null',
                            'injured_work': 'null', 'injured_education': 'null', 'injured_resident': 'null', 'injured_marriage': []}
            injured_info['injured_name'] = injuerd
            injured_list.append(injured_info)
    return injured_list


def _get_injured_birth(lines: List[str], injured_list) -> List[dict]:
    if injured_list == []:
        return injured_list
    birth_date = ''
    torsubline = 0
    birth_bool = False
    find_injured = False
    name = r'(原告)|(被害人)'
    for injured in injured_list:
        birth_date = None
        for line in lines:
            if line == '\n':
                continue
            find_injured = False
            keyObj = re.search((injured["injured_name"]).replace(
                '*', '某'), line.replace('*', '某'))
            keyObj2 = re.search(name, line)
            if keyObj is not None or keyObj2 is not None:
                line = re.split(r'[，：；。]', line)
                for subline in line:
                    torsubline += 1
                    keyObj = re.search((injured["injured_name"]).replace(
                        '*', '某'), subline.replace('*', '某'))
                    if keyObj is not None or find_injured:
                        torsubline = 0
                        find_injured = True
                        birth_date = pattern.search(subline)
                        birthbool2 = re.search(r'(出生|生于|生$)', subline)
                        if birth_date is not None and birthbool2 is not None:
                            birth_bool = True
                            injured["injured_birth"] = date_format(
                                birth_date[0])
                        if birth_bool:
                            break
                    if find_injured and torsubline > 7:
                        find_injured = False
                if birth_bool:
                    birth_bool = False
                    break
    return injured_list


def _get_injured_sex(lines: List[str], injured_list) -> List[dict]:
    if injured_list == []:
        return injured_list
    torsubline = 0
    sex_bool = False
    find_injured = False
    name = r'(原告)|(被害人)'
    for injured in injured_list:
        sex = None
        for line in lines:
            if line == '\n':
                continue
            find_injured = False
            # injured["injured_name"]=(injured["injured_name"]).replace('*','某')
            keyObj = re.search((injured["injured_name"]).replace(
                '*', '某'), line.replace('*', '某'))
            keyObj2 = re.search(name, line)
            if keyObj is not None or keyObj2 is not None:
                line = re.split(r'[，：；。]', line)
                for subline in line:
                    torsubline += 1
                    keyObj = re.search((injured["injured_name"]).replace(
                        '*', '某'), subline.replace('*', '某'))
                    if keyObj is not None or find_injured:
                        torsubline = 0
                        find_injured = True
                        sex = re.search(r'[男女]', subline)
                        if sex is not None and re.search(r'子女|女儿', subline) is None:
                            sex_bool = True
                            injured["injured_sex"] = sex[0]
                        if sex_bool:
                            break
                    if find_injured and torsubline > 7:
                        find_injured = False
                if sex_bool:
                    sex_bool = False
                    break
    return injured_list


def _get_injured_marri(lines: List[str], injured_list) -> List[dict]:
    if injured_list == []:
        return injured_list
    find_injured = False
    name = r'(原告)|([被受]害人)|(死者)'
    for injured in injured_list:
        for line in lines:
            if line == '\n':
                continue
            marri = re.search("婚育史", line)
            if marri is not None:
                line = re.split(r'[；。]', line)
                for subline in line:
                    marri = re.search("婚育史", subline)
                    if marri is not None:
                        keyObj = re.search((injured["injured_name"]).replace(
                            '*', '某'), subline.replace('*', '某'))
                        keyObj2 = re.search(name, subline)
                        if keyObj is not None or keyObj2 is not None:
                            find_injured = True
                            marriage = subline
                            injured["injured_marriage"].append(subline)
                            break
    return injured_list


def _get_injured_work(lines: List[str], injured_list, plaintiff_info) -> List[dict]:
    import jieba
    import jieba.posseg as pseg
    jieba.enable_paddle()
    if injured_list == []:
        return injured_list
    works = [r'务农|种地|工地|职员|保安|兼职|无业|无工作']
    name = r'(原告)|([被受]害人)|(死者)'
    # plaintiff_info = get_plaintiff_info(lines)
    for work in works:
        for line in lines:
            if line == '\n':
                continue
            injured_work = 'null'
            sublines = re.split(r'[。；，：]', line)
            for index, subline in enumerate(sublines):
                if re.search(r'第.+条|补助标准', subline) is not None:
                    continue
                here_u_a = False
                keyObj_e = re.search(work, subline)
                keyObj_justwork = re.search(r'工作', subline)
                if keyObj_justwork is not None or keyObj_e is not None:
                    if "无工作" in subline:
                        here_u_a = True
                    seg_list = pseg.cut(subline, use_paddle=True)
                    for seg in seg_list:
                        if seg.flag == 'ORG' or seg.flag == 'LOC' or seg.flag == 'nt' or seg.flag == 's':
                            here_u_a = True
                            break
                    if here_u_a or keyObj_e is not None:
                        injured_work = subline
                        for injured_info in injured_list:
                            in_for = False
                            for i in range(0, min(7, index)):
                                keyObj = re.search((injured_info["injured_name"]).replace(
                                    '*', '某'), sublines[index-i].replace('*', '某'))
                                keyObj2 = re.search(name, sublines[index-i])
                                if keyObj is not None or keyObj2 is not None:
                                    in_for = True
                                    break
                            if 1-in_for:
                                keyObj = re.search((injured_info["injured_name"]).replace(
                                    '*', '某'), subline.replace('*', '某'))
                                keyObj2 = re.search(name, subline)
                            if keyObj is not None:
                                if injured_info["injured_work"] == 'null':
                                    injured_info["injured_work"] = injured_work
                                    break
                            if keyObj2 is not None:
                                if injured_info["injured_work"] == 'null':
                                    for plaint in plaintiff_info:
                                        if injured_info["injured_name"] == plaint["plaintiff"] and '原告' in subline:
                                            injured_info["injured_work"] = injured_work
                                        elif injured_info["injured_name"] != plaint["plaintiff"] and '原告' not in subline:
                                            injured_info["injured_work"] = injured_work
    return injured_list


def _get_injured_edu(lines: List[str], injured_list) -> List[dict]:
    if injured_list == []:
        return injured_list
    education = r'初中|小学|高中|本科|文盲'
    name = r'([被受]害人)|(死者)'
    for line in lines:
        if line == '\n':
            continue
        keyObj = re.search(education, line)
        keyObj_wenhua = re.search(r'文[凭化盲]', line)
        if keyObj is not None and keyObj_wenhua is not None:
            sublines = re.split(r'[：；。]', line)
            for subline in sublines:
                breakit = True
                keyObj = re.search(education, subline)
                keyObj_wenhua = re.search(r'文[凭化盲]', subline)
                if keyObj is not None and keyObj_wenhua is not None:
                    if keyObj[0] == keyObj_wenhua[0]:
                        tmp_edu = keyObj[0]
                    else:
                        tmp_edu = keyObj[0]+keyObj_wenhua[0]
                    for injured_info in injured_list:
                        keyObj_name = re.search((injured_info["injured_name"]).replace(
                            '*', '某'), subline.replace('*', '某'))
                        keyObj2 = re.search(name, subline)
                        if keyObj_name is not None and injured_info["injured_name"] != '':
                            subsublines = (subline.split(
                                injured_info["injured_name"])[1]).split("，")
                            # subsublines=subline.split("，")
                            for sub in subsublines:
                                keyObj = re.search(education, sub)
                                keyObj_wenhua = re.search(r'文[凭化盲]', sub)
                                if keyObj is not None and keyObj_wenhua is not None:
                                    if keyObj[0] == keyObj_wenhua[0]:
                                        tmp_edu = keyObj[0]
                                    else:
                                        tmp_edu = keyObj[0]+keyObj_wenhua[0]
                                    injured_info["injured_education"] = tmp_edu
                                    breakit = True
                                    break
                        if 1-breakit and keyObj2 is not None:
                            for injured_info in injured_list:
                                keyObj = re.search((injured_info["injured_name"]).replace(
                                    '*', '某'), subline.replace('*', '某'))
                                if keyObj is not None and injured_info["injured_education"] != 'null':
                                    injured_info["injured_education"] = tmp_edu
                                    break
                        elif keyObj is None and keyObj2 is None and injured_info["injured_education"] == 'null':
                            injured_info["injured_education"] = tmp_edu
    return injured_list


def _get_injured_resdt(lines: List[str], injured_list) -> List[dict]:
    import jieba
    import jieba.posseg as pseg
    jieba.enable_paddle()
    if injured_list == []:
        return injured_list
    res = [r'(住(?![院宿]))|生活(?!费|来源|水平|自理)']  # ,r'(居委会)|[^农]村|县'
    relative = r'父|母|儿|兄|弟|姐|妹'
    includeres = r'与|和|跟'
    resdt = False
    breakall = True
    name = r'(原告)|([被受]害人)|(死者)'
    for r in res:
        for line in lines:
            if line == '\n':
                continue
            injured_resident = 'null'
            line = re.split(r'[。]', line)
            for l in line:
                breakit = True
                # sublines = re.split(r'[：；，]', l)
                # for subline in sublines:
                keyObj = re.search(r, l)
                keyObj_relative = re.search(relative, l)
                keyObj_include = re.search(includeres, l)
                if keyObj is not None and keyObj_relative is not None and keyObj_include is None:
                    continue
                elif keyObj is not None:
                    subline = re.sub(r'[\n\s]', '', l)
                    seg_list = pseg.cut(subline, use_paddle=True)
                    for seg in seg_list:
                        if seg.flag == 'ns' or seg.flag == 'nt' or seg.flag == 'LOC':
                            # injured_resident = sublines
                            resdt = True
                    if resdt:
                        resdt = False
                        for s in subline.split("，"):
                            if re.search(r, s) is not None:
                                injured_resident = s
                                break
                        for injured_info in injured_list:
                            is_split = True
                            keyObj = re.search((injured_info["injured_name"]).replace(
                                '*', '某'), l.replace('*', '某'))
                            keyObj2 = re.search(name, subline)
                            if keyObj is not None and injured_info["injured_name"] != '':
                                if injured_info["injured_resident"] == 'null':
                                    try:
                                        subline_use = subline.split(
                                            injured_info["injured_name"])[1]
                                    except Exception:
                                        is_split = False
                                        breakit = False
                                        injured_info["injured_resident"] = injured_resident
                                    if is_split:
                                        if injured_resident in subline_use:
                                            injured_info["injured_resident"] = injured_resident
                                            breakit = False
                            if breakit and keyObj2 is not None:
                                for injured_info in injured_list:
                                    keyObj = re.search((injured_info["injured_name"]).replace(
                                        '*', '某'), subline.replace('*', '某'))
                                    if keyObj is not None:
                                        break
                                if injured_info["injured_resident"] == 'null':
                                    try:
                                        subline_use = subline.split(
                                            injured_info["injured_name"])[1]
                                    except Exception:
                                        is_split = False
                                        injured_info["injured_resident"] = injured_resident
                                    if is_split:
                                        if injured_resident in subline_use:
                                            injured_info["injured_resident"] = injured_resident
                                break
        for injured_info in injured_list:
            if injured_info["injured_resident"] == 'null':
                breakall = False
                break
        if breakall:
            return injured_list
    return injured_list


def get_injured_info(lines: List[str]) -> List[dict]:
    plaintiff_info = get_plaintiff_info(lines)
    injured_list = _get_injured_name(lines, plaintiff_info)
    injured_list = _get_injured_birth(lines, injured_list)
    injured_list = _get_injured_sex(lines, injured_list)
    injured_list = _get_injured_marri(lines, injured_list)
    injured_list = _get_injured_work(lines, injured_list, plaintiff_info)
    injured_list = _get_injured_edu(lines, injured_list)
    injured_list = _get_injured_resdt(lines, injured_list)

    return injured_list

def get_plaintiff_info(lines: List[str], ined: bool = False) -> List[dict]:
    plaintiff_more_info = case_info.get_plaintiff_info_v1(lines)
    if len(plaintiff_more_info) != 0:
        plaintiff_more_info = _get_plaintiff_birsex(lines, plaintiff_more_info)
    if len(plaintiff_more_info) <= 1:
        ined = True
        for index, line in enumerate(lines):
            line = re.sub(r'[　\s+]', '', line)
            if re.search(r'审判[员|长]', line) is not None:
                if index <= 8 and not ined:
                    newlines = []
                    for newline in lines:
                        newline = re.split(r'。', newline)
                        newlines += newline
                    plaintiff_more_info = get_plaintiff_info(newlines, True)
                return plaintiff_more_info
    return plaintiff_more_info

def _get_plaintiff_birsex(lines: List[str], plaintiff_more_info) -> List[dict]:
    if plaintiff_more_info == []:
        return plaintiff_more_info
    birth_date = ''
    torsubline = 0
    sex_bool = False
    birth_bool = False
    find_plaintiff = False
    name = r'(原告)'
    for plaintiff_name in plaintiff_more_info:
        if "公司" in plaintiff_name['plaintiff']:
            continue
        plaintiff_name["plaintiff_birth"] = ''
        plaintiff_name["plaintiff_sex"] = ''
        birth_date = None
        sex = None
        for line in lines:
            if line == '\n':
                continue
            find_plaintiff = False
            # injured["injured_name"]=(injured["injured_name"]).replace('*','某')
            keyObj = re.search((plaintiff_name['plaintiff']).replace('*', '某'), line.replace('*', '某'))
            keyObj2 = re.search(name, line)
            if keyObj is not None or keyObj2 is not None:
                line = re.split(r'[，：；。]', line)
                for subline in line:
                    torsubline += 1
                    keyObj = re.search((plaintiff_name['plaintiff']).replace(
                        '*', '某'), subline.replace('*', '某'))
                    if keyObj is not None or find_plaintiff:
                        torsubline = 0
                        find_plaintiff = True
                        birth_date = pattern.search(subline)
                        birthbool2 = re.search(r'(出生|生于|生$)', subline)
                        sex = re.search(r'[男女]', subline)
                        if birth_date is not None and birthbool2 is not None:
                            birth_bool = True
                            if plaintiff_name["plaintiff_birth"] == '':
                                plaintiff_name["plaintiff_birth"] = date_format(
                                    birth_date[0])
                        if sex is not None and re.search(r'子女|女儿', subline) is None:
                            sex_bool = True
                            plaintiff_name["plaintiff_sex"] = sex[0]
                        if birth_bool and sex_bool:
                            break
                        if birthbool2 is not None and birth_date is None and plaintiff_name["plaintiff_birth"] == '':
                            birth_date = pattern_ym.search(subline)
                            if birth_date is not None:
                                plaintiff_name["plaintiff_birth"] = birth_date[0]
                                break
                        if birthbool2 is not None and birth_date is None and plaintiff_name["plaintiff_birth"] == '':
                            birth_date = pattern_year.search(subline)
                            if birth_date is not None:
                                plaintiff_name["plaintiff_birth"] = birth_date[0]
                                break
                    if find_plaintiff and torsubline > 2:
                        find_plaintiff = False
                if birth_bool and sex_bool:
                    birth_bool = False
                    sex_bool = False
                    break
    return plaintiff_more_info


def get_defendant_info(lines: List[str], ined: bool = False) -> List[dict]:
    defendant_more_info = case_info.get_defendant_info_v1(lines)
    if len(defendant_more_info) != 0:
        defendant_more_info = _get_defendant_birsex(lines, defendant_more_info)
    if len(defendant_more_info) < 1:
        ined = True
        for index, line in enumerate(lines):
            line = re.sub(r'[　\s+]', '', line)
            if re.search(r'审判[员|长]', line) is not None:
                if index <= 8 and not ined:
                    newlines = []
                    for newline in lines:
                        newline = re.split(r'。', newline)
                        newlines += newline
                    defendant_more_info = get_defendant_info(newlines, True)
                return defendant_more_info
    return defendant_more_info


def _get_defendant_birsex(lines: List[str], defendant_more_info) -> List[dict]:
    if defendant_more_info == []:
        return defendant_more_info
    birth_date = ''
    torsubline = 0
    sex_bool = False
    birth_bool = False
    find_defendant = False
    name = r'(被告)'
    for defendant_name in defendant_more_info:
        try:
            if "公司" in defendant_name['defendant']:
                continue
        except KeyError:
            continue
        defendant_name["defendant_birthday"] = ''
        defendant_name["defendant_sex"] = ''
        birth_date = None
        sex = None
        for line in lines:
            if line == '\n':
                continue
            find_defendant = False
            # injured["injured_name"]=(injured["injured_name"]).replace('*','某')
            keyObj = re.search((defendant_name['defendant']).replace('*', '某').replace(" ", "").replace("（", "").replace("）", "").replace("(", "").replace(")", ""), line.replace('*', '某'))
            keyObj2 = re.search(name, line)
            if keyObj is not None or keyObj2 is not None:
                line = re.split(r'[，：；。]', line)
                for subline in line:
                    torsubline += 1
                    keyObj = re.search((defendant_name['defendant']).replace(
                        '*', '某').replace(" ", "").replace("（", "").replace("）", "").replace("(", "").replace(")", ""), subline.replace('*', '某'))
                    if keyObj is not None or find_defendant:
                        torsubline = 0
                        find_defendant = True
                        birth_date = pattern.search(subline)
                        birthbool2 = re.search(r'(出生|生于|生$)', subline)
                        sex = re.search(r'[男女]', subline)
                        if birth_date is not None and birthbool2 is not None:
                            birth_bool = True
                            if defendant_name["defendant_birthday"] == '':
                                defendant_name["defendant_birthday"] = date_format(
                                    birth_date[0])
                        if sex is not None and re.search(r'子女|女儿', subline) is None:
                            sex_bool = True
                            defendant_name["defendant_sex"] = sex[0]
                        if birth_bool and sex_bool:
                            break
                        if birthbool2 is not None and birth_date is None and defendant_name["defendant_birthday"] == '':
                            birth_date = pattern_ym.search(subline)
                            if birth_date is not None:
                                defendant_name["defendant_birthday"] = birth_date[0]
                                break
                        if birthbool2 is not None and birth_date is None and defendant_name["defendant_birthday"] == '':
                            birth_date = pattern_year.search(subline)
                            if birth_date is not None:
                                defendant_name["defendant_birthday"] = birth_date[0]
                                break
                    if find_defendant and torsubline > 2:
                        find_defendant = False
                if birth_bool and sex_bool:
                    birth_bool = False
                    sex_bool = False
                    break
    return defendant_more_info