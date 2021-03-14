# 开发文档
## 概述
大部分使用正则方式进行匹配，争议焦点相关内容使用了BERT-逻辑回归模型
## 字段解析器
### 案件名称
直接从标题中获取
### 案号
使用正则表达式匹配`[（|()]\d{4}[）|)].+号`
### 年份
先找到案号，再用正则匹配`[（|(](\d{4})[）|)]`
### 案由
根据相关规定，案由是有限的，相关对应关系已整理好，保存在文件里，直接匹配是否出现即可
### 审判程序
根据案号判断，相关对应关系已整理好，保存在文件里
### 案件类型
根据案号判断，相关对应关系已整理好，保存在文件里
### 法院
正则匹配`(\S{1,10}(自治)?[省州市县区])+.{1,6}法院`
### 文书类型
根据案号判断，相关对应关系已整理好，保存在文件里
### 法官
正则匹配`(审判员)|[　\s]+`
### 书记
正则匹配`(书记员)|[　\s]+`
### 原告信息
NER模型+正则匹配：NER判断是否为人名、组织名等，正则判断为保险公司或者律所
### 被告信息
NER模型+正则匹配：NER判断是否为人名、组织名等，正则判断为保险公司或者律所
### 诉求
正则匹配：使用相关触发次词触发，再根据规律找到响应诉求
### 争议焦点
正则匹配：使用相关触发次词触发，再根据规律找到响应争议焦点
### 案件总结
先找到争议焦点，再使用seq_match模型找到争议焦点对应段落，再从对应段落中根据正则`《.+?》(第?[〇一二三四五六七八九十百千]+?条、?)*`找到相关法律法规；通过正则`予以(支持|认可|采纳)`和`不予?(支持|认可|采纳)`判断法院是否支持；其余信息为相关依据。