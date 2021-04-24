
#!/usr/bin/env python
import argparse
import json
import os
import json
from traceback import print_exc
import case_parsers

input_path = ""
output_path = ""
attrs = ['all', 'case_name', 'case_id', 'year', 'cause', 'trial_procedure',
         'case_type', 'court', 'document_type', 'judge', 'clerk', 'plaintiff_info', 'defendant_info', 'case_summary','filing_date','judgment_date','discharge_date','city_class','hospital','diagnosis','previous','accident_date','disable_assessment_date','injured_info','']

def process_one(file_name,lines):
    field_dict = {}
    #second requests are from 14
    for attr in attrs[-2:-1]:
        func = getattr(case_parsers, 'get_'+attr)
        ret = func(lines)
        field_dict[attr] = ret

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
