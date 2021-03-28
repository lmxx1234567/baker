# 'filing_date','judgment_date','discharge_date','city_class','hospital','diagnosis','previous'，
# 事故日期：accident_date
# 评残日期：disable_assessment_date
# 正则标准：年份必须是四位数，否则标准化时将出问题，年和月无所谓（XXXX年XX月XX日，XXXX/XX/XX, XXXX\XX\XX,XXXX年XX月XX号）
import re
from typing import List, Dict
import datetime

pattern = re.compile(
    '\d{2,4}[\.\-/年]{1}\d{1,2}[\.\-/月]{1}\d{1,2}[日号]{0,1}|[一二].{1,3}年.{1,2}月.{1,3}[日号]{1}')
pattern_accdate = re.compile(
    '[2].\d{1,3}[\.\-/年]{1}\d{1,2}[\.\-/月]{1}\d{1,2}[日号]{0,1}|[一二].{1,3}年.{1,2}月.{1,3}[日号]{1}')
replace_lists = [{'年': '-', '月': '-', '日': '', '\.': '-', '/': '-', '号': ''},
                 {'九': '9', '八': '8', '七': '7', '六': '6', '五': '5', '四': '4', '三': '3',
                     '二': '2', '一': '1', '元': '1', '○': '0', '〇': '0', '零': '0', 'O': '0'},
                 {'三十一': '31', '三十': '30', '二十九': '29', '二十八': '28', '二十七': '27', '二十六': '26', '二十五': '25', '二十四': '24', '二十三': '23', '二十二': '22', '二十一': '21', '二十': '20', '十九': '19', '十八': '18', '十七': '17', '十六': '16', '十五': '15', '十四': '14', '十三': '13', '十二': '12', '十一': '11', '十': '10', '九': '09', '八': '08', '七': '07', '六': '06', '五': '05', '四': '04', '三': '03', '二': '02', '一': '01', '元': '01'}]
pattern2 = re.compile(
    '[一二].{1,3}年.{1,2}月.{1,3}[日号]{1}')


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
    format_date = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2])).strftime(
        "%{0}-%m-%d".format('Y' if yearlen == 4 else 'y'))
    return format_date

# filing_date立案日期:‘立案’关键字段落寻找日期


def get_filing_date(lines: List[str]) -> str:
    filing_date = None
    for line in lines:
        if "立案" in line:
            line = re.split(r'[，：；。]', line)
            for subline in line:
                if "立案" in subline:
                    filing_date = pattern.search(subline)
                if filing_date is not None:
                    break
        if filing_date is not None:
            filing_date = date_format(filing_date[0])
            break
        else:
            if "受理" in line:
                line = re.split(r'[，：；。]', line)
                for subline in line:
                    if "受理" in subline:
                        filing_date = pattern.search(subline)
                    if filing_date is not None:
                        break
            if filing_date is not None:
                a = filing_date[0]
                filing_date = date_format(filing_date[0])
                break
    return filing_date

# 文末判决日期


def get_judgment_date(lines: List[str]) -> str:
    for line in reversed(lines):
        judgment_date = pattern2.search(line)
        if judgment_date is not None:
            judgment_date = date_format(judgment_date[0])
            break
    return judgment_date

# 出院日期:于...出院;...出院


def get_discharge_date(lines: List[str]) -> str:
    discharge_date = None
    for line in lines:
        if "出院" in line:
            line = re.split(r'[，：；。]', line)
            for subline in line:
                if "出院" in subline:
                    discharge_date = pattern.search(subline)
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
        if "人民法院" in line:
            line = re.split(r'[，：；。\s+]', line)
            for subline in line:
                if "人民法院" in subline:
                    seg_list = pseg.cut(subline, use_paddle=True)
                    for seg in seg_list:
                        if seg.flag == 'ns' or seg.flag == 'nt' or seg.flag == 'ORG':
                            court_name = re.sub(r'[，：；。]', '', seg.word)
                            break
                if court_name is not None:
                    break
        if court_name is not None:  # 进行地市分级
            city = re.sub("人民法院", '', court_name)
            citylist.append(city)
            city_class = cpca.transform(citylist)
            break
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
        if "医院" in line:
            line = re.split(r'[，：；。\s+]', line)
            for subline in line:
                if "医院" in subline:
                    seg_list = pseg.cut(subline, use_paddle=True)
                    for seg in seg_list:
                        if (seg.flag == 'ns' or seg.flag == 'nt' or seg.flag == 'ORG') and ("医院" in (seg.word)):
                            if "转" in subline:
                                # transfer = re.sub(r'[，：；。]', '', seg.word)
                                transfer = (re.split("医院", seg.word))[0]+"医院"
                                transfer_hospital.append(transfer)
                            else:
                                # treatment = re.sub(r'[，：；。]', '', seg.word)
                                treatment = (re.split("医院", seg.word))[0]+"医院"
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
    multidiagnosis = []
    # 存储所有带有“诊断”的list
    for line in lines:
        if "诊断" in line:
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
                half = re.split("既往", period_subline)
                # period_subline = re.split(r'[，：；]', period_subline)
                period_subline = re.findall(
                    '.*?[：；]', period_subline)  # 更精细的时候要加上逗号
                for comma_index, comma_subline in enumerate(period_subline):
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
                line = (re.split(p, line))[1]
                sublines0 = re.split(r'[，：:；。]', line)
                try:
                    if '\n' in line[1]:
                        nextline = True
                        continue
                except IndexError:
                    nextline = True
                    continue
                torline += 1
                for subline in sublines0:
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
            keyObj = re.search(p, line)
            if keyObj is not None:
                line = re.split(r'[；。]', line)
                for subline in line:
                    keyObj = re.search(p, subline)
                    if keyObj is not None:
                        disable_assessment = pattern.search(subline)
                    if disable_assessment is not None:
                        return date_format(disable_assessment[0])
    return disable_assessment
