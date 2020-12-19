# -*- coding:utf-8 -*-

import json
from HTMLParser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc
import codecs


class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')
        elif tag == 'div':  # add by viv
            self.__text.append('\n')
        # elif tag == 'span':
        #     self.__text.append('_')


    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')
        if tag == 'div':
            self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()




def dehtml(text):
    try:
        parser = _DeHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except:
        print_exc(file=stderr)
        return text

def process_json_line(f_json):
    with open(f_json, 'r') as f:
        for line in f:
            # 解析json
            d_sub_res = json.loads(line)  # 返回顺序字典

            # 获取文件名
            file_name = d_sub_res['title']
            file_name = dehtml(file_name)
            file_name = file_name.replace(' ', '')
            file_name = file_name + '.txt'

            # 获取内容
            content = d_sub_res['content']
            content = dehtml(content)
            content = content.replace(' ', '')

            # 写文件
            f = codecs.open(file_name, 'w', 'utf-8')
            f.write(content)
            f.close()
            # print file_name, ' finish!\n'
    return file_name



# if __name__ == '__main__':
#     #process_json_line("wenshu_test3.json")
#     process_json_line('wenshu_20201205_jiaodian.json')
