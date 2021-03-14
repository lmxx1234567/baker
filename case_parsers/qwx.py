# 'filing_date','judgment_date','discharge_date','city_class','hospital'
# 正则标准：年份必须是四位数，否则标准化时将出问题，年和月无所谓（XXXX年XX月XX日，XXXX/XX/XX, XXXX\XX\XX,XXXX年XX月XX号）
import re
import csv
from typing import List, Tuple
import itertools
import datetime
from . import schema, similar, SEQ_MODEL_AVALIABLE
from case_parsers.seq_match import seq_match, seq_match_multiple

pattern = re.compile(
    '\d{2,4}[\.\-/年]{1}\d{1,2}[\.\-/月]{1}\d{1,2}[日号]{0,1}|[一二].{1,3}年.{1,2}月.{1,3}[日号]{1}')
replace_lists = [{'年': '-', '月': '-', '日': '', '\.': '-', '/': '-', '号': ''},
                 {'九': '9', '八': '8', '七': '7', '六': '6', '五': '5', '四': '4', '三': '3',
                     '二': '2', '一': '1', '元': '1', '○': '0', '〇': '0', '零': '0'},
                 {'三十一': '31', '三十': '30', '二十九': '29', '二十八': '28', '二十七': '27', '二十六': '26', '二十五': '25', '二十四': '24', '二十三': '23', '二十二': '22', '二十一': '21', '二十': '20', '十九': '19', '十八': '18', '十七': '17', '十六': '16', '十五': '15', '十四': '14', '十三': '13', '十二': '12', '十一': '11', '十': '10', '九': '09', '八': '08', '七': '07', '六': '06', '五': '05', '四': '04', '三': '03', '二': '02', '一': '01', '元': '01'}]


def date_format(raw_date: str):
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
    return filing_date

# 文末判决日期


def get_judgment_date(lines: List[str]) -> str:
    for line in reversed(lines):
        judgment_date = pattern.search(line)
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


def get_city_class(lines: List[str]):
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


def get_hospital(lines: List[str]) -> str:
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
    return treatment_hospital
