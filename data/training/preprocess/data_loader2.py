# encoding: utf-8
import csv
import os
import numpy as np
import random
import json

def data_loader2(str):
    example2_file = str
    tag_data = []
    find_pos = {}
    pos_cause = []
    debug4=False
    debug3=False
    debug2=False
    debug1=False
    pos_concaus = []
    result = {}
    with open(example2_file) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        tag_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:  # 将csv 文件中的数据保存到tag_data中
            tag_data.append(row)
    tag_header = np.array(tag_header)
    lines = len(tag_data)
    # 把每一行拆成新list
    for line in range(0, lines):
        con = {}
        con['judgement'] = tag_data[line][3]
        txt_name = "input2/"+tag_data[line][0]+".txt"
        con_content = tag_data[line][1]
        try:
            txtfile=open(txt_name, "r")
        except:
            # print(txt_name)
            continue
        with open(txt_name, "r") as txtfile:
            wenshu_data = txtfile.read()  # 读取文件
            sublines = wenshu_data.split("\n")
            pos_concaus = []
            for subline_num, subline in enumerate(sublines):
                # 打开下面，即找争议焦点位置：
                if tag_data[line][2] in subline:
                    len_contsy = len(tag_data[line][2])
                    st_index = subline.find(tag_data[line][2])
                    con = {'line': subline_num, 'start': st_index,
                           'end': st_index+len_contsy}
                # 找标注bug用，判断是否有空行（前面的循环已经用\n分割）
                # if tag_data[line][4] == "":
                #     debug4=True
                #     print("4 空行："+txt_name)
                # if tag_data[line][3] == "" and debug4 == False:
                #     debug3=True
                #     print("3 空行："+txt_name)
                # if tag_data[line][2] == "" and debug3 == False:
                #     debug2=True
                #     print("2 空行："+txt_name)
                # if tag_data[line][1] == "" and debug2 == False:
                #     debug1=True
                #     print("1 空行："+txt_name)

                # 打开下面，即找cause位置：
                if tag_data[line][4] in subline:
                    len_contsy = len(tag_data[line][4])
                    st_index = subline.find(tag_data[line][4])
                    pos_concau = {'line': subline_num,
                                  'start': st_index, 'end': st_index+len_contsy}
                    con['causes'] = [pos_concau]
                else:
                    tmps = tag_data[line][4].split('\n')
                    for tmp in tmps:
                        if tmp in subline:
                            len_contsy = len(tmp)
                            st_index = subline.find(tmp)
                            pos_concaus.append(
                                {'line': subline_num, 'start': st_index, 'end': st_index+len_contsy})
                            # 找标注bug用，len_contsy==0代表没找到
                            # if len_contsy==0 and debug1 == False and debug2 == False and debug3 == False and debug4 == False:
                            #     print("0and0:"+txt_name)
                            con['causes'] = pos_concaus
        if txt_name in result:
            result[txt_name].append(con)
        else:
            result[txt_name] = [con]
    return result
print(json.dumps(data_loader2('tag4train.csv')))
# data_loader2('tag4train.csv')
# print(tag_data[line][1][0])
