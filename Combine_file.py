
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

input_path = ""
output_path = ""


def process_one(file_name,lines):
    field_dict = {}
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
    with open(output_path + "/"+file_name.split('.')[0] + ".json", 'w', encoding="utf-8") as json_file:
        json_file.write(json_str)
    # print(wenshu_name)
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Legal document parser')
    parser.add_argument('input', help='Path to legal document')
    parser.add_argument('output', help='Path to legal document')
    args = parser.parse_args()
    input_path = args.input
    output_path = args.output
    num = 0
    for filename in os.listdir(args.input):
        try:
            lines = []
            if "txt" in filename:
                with open(input_path+"/"+filename) as f:
                    lines = f.readlines()
                print(filename)
                process_one(filename,lines)
                num = num + 1

                # break
        except Exception as e:
            print(num)
            print(e)

    output_str = "共处理"+str(num)+"条数据"
    print(output_str)  
