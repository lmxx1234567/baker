import argparse
import json
import re
import os
from case_parsers import case_info

attrs = ['all', 'case_name', 'case_id', 'year', 'cause', 'trial_procedure',
         'case_type', 'court', 'document_type', 'judge', 'clerk', 'plaintiff_info', 'defendant_info', 'case_summary']

kv = {"fee_medical": "医疗费", "fee_mess": "住院伙食补助", "fee_nurse": "护理费",
      "fee_nutrition": "营养费", "fee_post_cure": "后期治疗费",
      "fee_loss_working": "误工费", "fee_traffic": "交通费",
      "fee_disable": "残疾赔偿金", "fee_death": "死亡赔偿金",
      "fee_bury": "丧葬费", "fee_life": "被抚养人生活费",
      "fee_trafic_for_process_bury": "处理丧葬人员的交通费",
      "fee_loss_working_for_process_bury": "处理丧葬人员的误工费",
      "fee_mind": "精神抚慰金", "fee_appraise": "鉴定费",
      "days": "天数", "criterion": "标准", "sum_of_money": "总金额",
      "years": "年限", "disable_level": "伤残等级", "percent": "百分比"}
word2num = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
            "十": 10, "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
            "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20}


def replace_commas(s):
    """去除字符串中数字间的逗号
    :param s: string
        待处理字符串
    :return: string
        去掉数字间逗号的字符串
    """
    s = s.replace(',', '，')
    p = re.compile(r'\d，\d')
    while True:
        m = p.search(s)
        if m:
            mm = m.group()
            s = s.replace(mm, mm.replace('，', ''))
        else:
            break
    return s


def get_medical(lines):
    """提取文档中医疗费的总金额
    :param document: docx.Document
        文档对象
    :return: dict
        字典，存放医疗费的总金额
    """
    medical_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    for line in lines:
        # line = document.paragraphs[i].text.strip()
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "医疗费" in line and flag:
            # 先去除数字间的逗号
            line = replace_commas(line)
            temp = re.findall(r'医疗费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                medical_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出与医疗费直接有关的句子
            match_result = re.findall(r'医疗费[^，、。]*-?\d+\.?\d*e?-?\d*?元', line)
            # 从该句子中提取出数字
            if match_result:
                medical_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元', match_result[0])[0]
            if "sum_of_money" in medical_fee:
                break
    return medical_fee


def get_mess(lines):
    """提取文档中伙食补助信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，伙食补助信息
    """
    mess_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
        # line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "住院伙食补助" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'住院伙食补助.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                mess_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出费用标准
            criterion = re.findall(r'住院伙食补助.*-?\d+\.?\d*e?-?\d*?元/[日天月年]', line)
            if criterion and "criterion" not in mess_fee:
                mess_fee["criterion"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元/[日天月年]', criterion[0])[0]
            # 提取出住院天数
            days = re.findall(r'住院伙食补助.*-?\d+\.?\d*e?-?\d*?[日天]', line)
            if days and "days" not in mess_fee:
                mess_fee["days"] = re.findall(r'-?\d+\.?\d*e?-?\d*?[日天]', days[0])[0]
            # 提取总花费
            fee = re.findall(r'住院伙食补助.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in mess_fee:
                mess_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in mess_fee:
                break
    return mess_fee


def get_nutrition(lines):
    """提取文档中的营养费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，营养费信息
    """
    nutrition_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "营养费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'营养费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                nutrition_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出费用标准
            criterion = re.findall(r'营养费.*-?\d+\.?\d*e?-?\d*?元/[日天月年]', line)
            if criterion and "criterion" not in nutrition_fee:
                nutrition_fee["criterion"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元/[日天月年]', criterion[0])[0]
            # 提取出住院天数
            days = re.findall(r'营养期.{0,1}-?\d+\.?\d*e?-?\d*?[日天]', line)
            if days and "days" not in nutrition_fee:
                nutrition_fee["days"] = re.findall(r'-?\d+\.?\d*e?-?\d*?[日天]', days[0])[0]
            # 提取总花费
            fee = re.findall(r'营养费.*-?\d+\.?\d*e?-?\d*?元', line)
            if fee and "sum_of_money" not in nutrition_fee:
                nutrition_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in nutrition_fee:
                break
    return nutrition_fee


def get_post_cure(lines):
    """提取文档中的后期治疗费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，后期治疗费信息
    """
    post_cur_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "后期治疗费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'后期治疗费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                post_cur_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取总花费
            fee = re.findall(r'后期治疗费.*-?\d+\.?\d*e?-?\d*?元', line)
            if fee and "sum_of_money" not in post_cur_fee:
                post_cur_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in post_cur_fee:
                break
    return post_cur_fee


def get_nurse(lines):
    """提取文档中的护理费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，护理费信息
    """
    nurse_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "护理费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'护理费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                nurse_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出费用标准
            criterion = re.findall(r'护理费.*-?\d+\.?\d*e?-?\d*?元/[日天月年]', line)
            if criterion and "criterion" not in nurse_fee:
                nurse_fee["criterion"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元/[日天月年]', criterion[0])[0]
            # 提取出住院天数
            days = re.findall(r'护理期.{0,1}-?\d+\.?\d*e?-?\d*?[日天]', line)
            if days and "days" not in nurse_fee:
                nurse_fee["days"] = re.findall(r'-?\d+\.?\d*e?-?\d*?[日天]', days[0])[0]
            else:
                temp = re.findall(r'-?\d+\.?\d*e?-?\d*?[日天]', line)
                if temp:
                    nurse_fee["days"] = temp[0]
            # 提取总花费
            fee = re.findall(r'护理费.*-?\d+\.?\d*e?-?\d*?元', line)
            if fee and "sum_of_money" not in nurse_fee:
                nurse_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in nurse_fee:
                break
    return nurse_fee


def get_loss_working(lines):
    """提取文档中的误工信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，误工损失信息
    """
    loss_working_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "误工费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'误工费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                loss_working_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出费用标准
            criterion = re.findall(r'误工费.*-?\d+\.?\d*e?-?\d*?元/[日天月年]', line)
            if criterion and "criterion" not in loss_working_fee:
                loss_working_fee["criterion"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元/[日天月年]', criterion[0])[0]
            # 提取出误工天数
            days = re.findall(r'误工费.*-?\d+\.?\d*e?-?\d*?天', line)
            if days and "days" not in loss_working_fee:
                loss_working_fee["days"] = re.findall(r'-?\d+\.?\d*e?-?\d*?[日天]', days[0])[-1]
            # 提取总花费
            fee = re.findall(r'误工费.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in loss_working_fee:
                loss_working_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in loss_working_fee:
                break
    return loss_working_fee


def get_traffic(lines):
    """提取文档中的交通费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，交通费信息
    """
    traffic_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "交通费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'交通费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                traffic_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出费用标准
            criterion = re.findall(r'交通费.*-?\d+\.?\d*e?-?\d*?元/[日天月年]', line)
            if criterion and "criterion" not in traffic_fee:
                traffic_fee["criterion"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元/[日天月年]', criterion[0])[0]
            # 提取出误工天数
            days = re.findall(r'交通费.*-?\d+\.?\d*e?-?\d*?[日天]', line)
            if days and "days" not in traffic_fee:
                traffic_fee["days"] = re.findall(r'-?\d+\.?\d*e?-?\d*?[日天]', days[0])[0]
            # 提取总花费
            fee = re.findall(r'交通费.*-?\d+\.?\d*e?-?\d*?元[^/]{0}', line)
            if fee and "sum_of_money" not in traffic_fee:
                traffic_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in traffic_fee:
                break
    return traffic_fee


def get_disable(lines):
    """提取文档中的残疾赔偿金信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，残疾赔偿金信息
    """
    disable_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "残疾赔偿金" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'残疾赔偿金.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                disable_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出费用标准
            # 先定位到有关键词的句子
            criterion = re.findall(r'残疾赔偿金.*-?\d+\.?\d*e?-?\d*?元/[日天月年]', line)
            # 再提取信息
            if criterion and "criterion" not in disable_fee:
                disable_fee["criterion"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元/[日天月年]', criterion[0])[0]
            # 提取出年限
            years = re.findall(r'残疾赔偿金.*-?\d+\.?\d*e?-?\d*?年', line)
            if years and "years" not in disable_fee:
                temp_years = re.findall(r'-?\d+\.?\d*e?-?\d*?年', years[0])
                temp_year = temp_years[0]
                for temp_year in temp_years:
                    if len(temp_year) <= 3:
                        break
                disable_fee["years"] = temp_year
            # 提取出赔付比例百分比
            percent = re.findall(r'残疾赔偿金.*-?\d+\.?\d*e?-?\d*?%', line)
            if percent and "percent" not in disable_fee:
                disable_fee["percent"] = re.findall(r'-?\d+\.?\d*e?-?\d*?%', percent[0])[0]
            # 提取出伤残等级
            level = re.findall(r'残疾赔偿金.*[0-9一二三四五六七八九十]级', line)
            if level and "disable_level" not in disable_fee:
                disable_fee["disable_level"] = re.findall(r'[0-9一二三四五六七八九十]级', level[0])[0]
            # 提取总金额
            fee = re.findall(r'残疾赔偿金.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in disable_fee:
                disable_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in disable_fee:
                break
    return disable_fee


def get_death(lines):
    """提取文档中的残疾赔偿金信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，死亡赔偿金信息
    """
    death_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "死亡赔偿金" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'死亡赔偿金.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                death_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取出费用标准
            criterion = re.findall(r'死亡赔偿金.*-?\d+\.?\d*e?-?\d*?元/[日天月年]', line)
            if criterion and "criterion" not in death_fee:
                death_fee["criterion"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元/[日天月年]', criterion[0])[0]
            # 提取出年限
            years = re.findall(r'死亡赔偿金.*-?\d+\.?\d*e?-?\d*?年', line)
            if years and "years" not in death_fee:
                temp_years = re.findall(r'-?\d+\.?\d*e?-?\d*?年', years[0])
                temp_year = temp_years[0]
                for temp_year in temp_years:
                    if len(temp_year) <= 3:
                        break
                death_fee["years"] = temp_year
            # 提取总金额
            fee = re.findall(r'死亡赔偿金.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in death_fee and "计" not in fee[0]:
                death_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in death_fee:
                break
    return death_fee


def get_bury(lines):
    """提取文档中的丧葬费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，丧葬费信息
    """
    bury_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
        # line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "丧葬费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'丧葬费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                bury_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取总金额
            fee = re.findall(r'丧葬费.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in bury_fee and "计" not in fee[0]:
                bury_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in bury_fee:
                break
    return bury_fee


def get_life(lines):
    """提取文档中的被抚养人生活费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，被抚养人生活费信息
    """
    life_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "被抚养人生活费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'被抚养人生活费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                life_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取总金额
            fee = re.findall(r'被抚养人生活费.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in life_fee:
                life_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in life_fee:
                break
    return life_fee


def get_mind(lines):
    """提取文档中的精神抚慰金信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，精神抚慰金信息
    """
    mind_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "精神抚慰金" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'精神抚慰金.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                mind_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取总金额
            fee = re.findall(r'精神抚慰金.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in mind_fee:
                mind_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            break
    return mind_fee


def get_traffic_for_process_bury(lines):
    """提取文档中的处理丧葬人员的交通费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，处理丧葬人员的交通费信息
    """
    traffic_for_process_bury_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if flag:
            line = replace_commas(line)
            temp = re.findall(r'处理事故及办理丧葬事宜人员交通费-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                traffic_for_process_bury_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取总金额
            fee = re.findall(r'处理.*丧葬.*人员.*交通费.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in traffic_for_process_bury_fee:
                traffic_for_process_bury_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in traffic_for_process_bury_fee:
                break
    return traffic_for_process_bury_fee


def get_loss_working_for_process_bury(lines):
    """提取文档中的处理丧葬人员的交通费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，处理丧葬人员的交通费信息
    """
    loss_working_for_process_bury_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if flag:
            line = replace_commas(line)
            temp = re.findall(r'处理丧葬人员的误工费.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                loss_working_for_process_bury_fee["总金额"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取总金额
            fee = re.findall(r'处理.*丧葬.*人员.*误工费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in loss_working_for_process_bury_fee:
                loss_working_for_process_bury_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            if "sum_of_money" in loss_working_for_process_bury_fee:
                break
    return loss_working_for_process_bury_fee


def get_appraise(lines):
    """提取文档中的鉴定费信息
    :param document: docx.Document
        文档对象
    :return: dict
        字典，鉴定费信息
    """
    appraise_fee = dict()
    flag = False
    # for i in range(len(document.paragraphs)):
    #     line = document.paragraphs[i].text.strip()
    for line in lines:
        if not line:
            continue
        if "本院认为" in line:
            flag = True
        if "鉴定费" in line and flag:
            line = replace_commas(line)
            temp = re.findall(r'鉴定费.{0,1,2,3}-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if temp:
                appraise_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', temp[0])[0]
                break
            # 提取总金额
            fee = re.findall(r'鉴定费.*-?\d+\.?\d*e?-?\d*?元(?!/)', line)
            if fee and "sum_of_money" not in appraise_fee:
                appraise_fee["sum_of_money"] = re.findall(r'-?\d+\.?\d*e?-?\d*?元(?!/)', fee[0])[0]
            break
    return appraise_fee