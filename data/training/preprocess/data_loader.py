# encoding: utf-8
import csv
import os
import numpy as np
import random
import json

def data_loader(str):
    example2_file = str
    tag_data = []
    find_pos = {}
    pos_cause = []
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
        txt_name = tag_data[line][0]
        con_content = tag_data[line][1]
        with open(txt_name, "r") as txtfile:
            wenshu_data = txtfile.read()  # 读取文件
            sublines = wenshu_data.split("\n")
            pos_concaus = []
            for subline_num, subline in enumerate(sublines):
                # 打开下面，即找争议焦点位置：
                if tag_data[line][1] in subline:
                    len_contsy = len(tag_data[line][1])
                    st_index = subline.find(tag_data[line][1])
                    con = {'line': subline_num, 'start': st_index,
                           'end': st_index+len_contsy}
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
                            con['causes'] = pos_concaus
        if txt_name in result:
            result[txt_name].append(con)
        else:
            result[txt_name] = [con]
    return result
# print(json.dumps(data_loader('example0112.csv')))
# print(tag_data[line][1][0])
