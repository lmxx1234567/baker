#!/usr/bin/env python
import pymongo
import argparse
import json
import re
import os
from case_parsers import case_info
from fee_field import *
import json
from HTMLParser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc
import codecs
from json_2_txt import *


output_path = ""


def process_one(input_str,index):
    field_dict = {}
     # 解析json
    # d_sub_res = json.loads(input_str)  # 返回顺序字典
    d_sub_res = input_str
    # 获取文件名
    wenshu_name = d_sub_res['title']
    wenshu_name = dehtml(wenshu_name)
    wenshu_name = wenshu_name.replace(' ', '')
    # 获取内容
    wenshu_content = d_sub_res['content']
    wenshu_content = dehtml(wenshu_content)
    wenshu_content = wenshu_content.replace(' ', '')
    # ID
    # wenshu_id = d_sub_res['_id']
    wenshu_id_2 = d_sub_res['wenshu_id']
    # Time
    wenshu_time = d_sub_res['sentence_date']
    # 打印文件名称
    print(wenshu_name)
    print(wenshu_id_2)
    # 写文件
    # with open(output_path + "/"+wenshu_name+".txt", 'w', encoding="utf-8") as txt_file:
    with open(output_path + "/"+str(index)+".txt", 'w', encoding="utf-8") as txt_file:
        txt_file.write(wenshu_content)

    # field_dict["wenshu_id_1"] = wenshu_id
    field_dict["wenshu_id_2"] = wenshu_id_2
    field_dict["wenshu_time"] = wenshu_time
    field_dict["wenshu_content"] = wenshu_content
    lines = wenshu_content.split("\n")
    for attr in attrs[1:]:
        module = __import__('case_parsers', fromlist=[
                            'case_info']).case_info
        func = getattr(module, 'get_'+attr)
        ret = func(lines)
        field_dict[attr] = ret
    field_dict["fee_medical"] = get_medical(lines)
    field_dict["fee_mess"] = get_mess(lines)
    field_dict["fee_nurse"] = get_nurse(lines)
    field_dict["fee_nutrition"] = get_nutrition(lines)
    field_dict["fee_post_cure"] = get_post_cure(lines)
    field_dict["fee_loss_working"] = get_loss_working(lines)
    field_dict["fee_traffic"] = get_traffic(lines)
    field_dict["fee_disable"] = get_disable(lines)
    field_dict["fee_death"] = get_death(lines)
    field_dict["fee_bury"] = get_bury(lines)
    field_dict["fee_life"] = get_life(lines)
    field_dict["fee_traffic_for_process_bury"] = get_traffic_for_process_bury(lines)
    field_dict["fee_loss_working_for_process_bury"] = get_loss_working_for_process_bury(lines)
    field_dict["fee_mind"] = get_mind(lines)
    field_dict["fee_appraise"] = get_appraise(lines)

    # print(field_dict)
    json_str = json.dumps(field_dict, indent=4, ensure_ascii=False)
    
    # with open(output_path + "/"+wenshu_name + ".json", 'w', encoding="utf-8") as json_file:
    with open(output_path + "/"+str(index) + ".json", 'w', encoding="utf-8") as json_file:
        json_file.write(json_str)
    
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Legal document parser')
    parser.add_argument('output', help='Path to legal document')
    args = parser.parse_args()
    output_path = args.output

    myclient = pymongo.MongoClient("mongodb://root:ziku2020@127.0.0.1:27017")
    mydb = myclient["insurance"]       #test-db是数据库名称 
    mycol = mydb["wenshu"]    #cust_refund是数据库的中一个数据表
    index = 0
    filter = {}
    # content = "争议焦点"
    keyword = "931d7bf6253749849111ac8c00372722"
    condition = {}
    condition['$regex'] = keyword
    filter["wenshu_id"] = condition
    output = ""
    num = 0
    for x in mycol.find():
        try:
            # print(type(x))
            process_one(x,num)
            num = num + 1
        except Exception as e:
            # print(num)
            print(e)
        # break
        # if num == 150:
        #     break  
    myclient.close()

    output_str = "共处理"+str(num)+"条数据"
    print(output_str)  
