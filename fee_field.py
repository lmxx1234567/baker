import re

# 各种费用
FeeType = ["medical", "mess", "nurse", "nutrition", "post_cure", "loss_working",
           "traffic", "disable", "death", "bury", "life", "traffic_for_process_bury",
           "loss_working_for_process_bury", "mind", "appraise",
           "total_loss", "appeal", "acceptance"]
# 法条
Field1 = ["legal_provision"]
# 判决金额、诉求金额、鉴定信息、受理费、非医保用药、免赔意见、扣减率
Field2 = ["appraise_info", "non_medical_insurance", "franchise", "discount_rate"]
kv = {
      # ================= 费用大类 =================
      "medical": "医疗费",
      "mess": "住院伙食补助",
      "nurse": "护理费",
      "nutrition": "营养费",
      "post_cure": "后期治疗费",
      "loss_working": "误工费",
      "traffic": "交通费",
      "disable": "残疾赔偿金",
      "death": "死亡赔偿金",
      "bury": "丧葬费",
      "life": "被抚养人生活费",
      "traffic_for_process_bury": "处理丧葬人员的交通费",
      "loss_working_for_process_bury": "处理丧葬人员的误工费",
      "mind": "精神抚慰金",
      "appraise": "鉴定费",
      "acceptance": "受理费",
      "medical_ci": "交强医疗",
      "death_disable_ci": "交强死残",
      "property_damage": "财产损失",
      "paramedic": "护理人员",
      # ================= 费用明细 =================
      "appeal_money": "诉求费用",
      "judge_money": "判决费用",
      "argued_money": "辩称费用",
      "cause": "诉求",
      "argue": "辩称",
      "basis": "相关法条",
      "evidence": "证据",
      # ================= 其他 =================
      "total_loss": "金额合计",
      "appeal": "诉求金额",
      "legal_provision": "法律条文",
      "appraise_info": "鉴定信息",
      "appraise_office": "鉴定所",
      "appraise_id": "鉴定书编号",
      "appraise_content": "鉴定内容",
      "non_medical_insurance": "非医保用药",
      "franchise": "免赔意见",
      "discount_rate": "扣减率"}

EVIDENCE_KEY_WORDS = {
    "医疗费": ["门诊收费票据", "门诊发票", "门诊收据", "医疗费发票", "门诊票据", "发票", "票据",
            "医疗发票", "医疗票据", "医疗费票据", "药店票据", "病情处理意见书", "诊断证明",
            "疾病诊断证明书", "病情证明书", "检查报告书", "住院病例", "住院病历",
            "病历", "住院病案", "住院收费收据", "住院结算凭证", "住院收费票据",
            "费用清单", "用药明细", "费用明细清单", "费用结算清单", "病情处理意见书",
            "入院通知单", "指定医院就诊证明", "入院证", "入院记录", "出院证", "住院记录",
            "出院小结", "诊断证明", "疾病诊断证明书", "出院病情证明书", "病情证明书",
            "出院诊断证明书", "收款凭证", "收据", "欠费证明"],
    "伙食补助": [],
    "护理费": ["鉴定意见书", "鉴定所鉴定意见书", "鉴定报告", "司法鉴定意见书", "鉴定书",
            "发票", "护理费发票", "护理合同", "护理人员的工资流水", "银行流水", "务工证明",
            "工资损失证明", "陪护协议", "陪护费发票", "护理人员身份证明", "收据", "欠费证明",
            "护理费协议", "完税证明"],
    "营养费": ["出院医嘱及建议", "出院小结", "出院记录", "鉴定所鉴定意见书",
            "鉴定意见书", "鉴定报告", "司法鉴定意见书", "鉴定书"],
    "后期治疗费": ["出院医嘱及建议", "出院小结", "药房购药票据", "鉴定所鉴定意见书", "发票",
              "鉴定意见书", "鉴定报告", "司法鉴定意见书", "鉴定书", "收据", "欠费证明"],
    "误工费": ["农村土地承包经营权证", "鱼池承包合同", "村民委员会证明", "村委会证明",
            "户口本", "身份信息户籍函", "户口册", "营业执照", "员工入职登记表",
            "人员名册", "工资流水", "请假证明", "工资表", "劳动合同", "鉴定所鉴定意见书",
            "鉴定意见书", "鉴定报告", "司法鉴定意见书", "鉴定书", "工资损失证明", "务工损失证明"],
    "交通费": ["火车票", "高速费收据", "汽车车票", "汽车票保险单"],
    "残疾赔偿金": ["鉴定意见书", "鉴定所鉴定意见书", "鉴定报告", "司法鉴定意见书", "鉴定书",
              "商品房买卖合同", "房地证", "不动产登记证", "居住证明", "村民委员会证明",
              "村委会证明", "营业执照", "结婚证", "劳动合同", "工资银行流水明细",
              "居民身份证", "户口本", "身份信息户籍函", "户口册", "社保缴费记录",
              "土地使用权证"],
    "死亡赔偿金": ["鉴定意见书", "鉴定所鉴定意见书", "鉴定报告", "司法鉴定意见书", "鉴定书",
              "居民死亡医学证明（推断）书", "死亡医学证明推断书", "火化证明", "遗体火化证明",
              "户口注销证明", "死亡注销户口证明", "商品房买卖合同", "房地证", "不动产登记证",
              "居住证明", "村民委员会证明", "村委会证明", "营业执照", "结婚证", "劳动合同",
              "工资银行流水明细", "居民身份证", "户口本", "身份信息户籍函", "户口册",
              "社保缴费记录", "土地使用权证"],
    "丧葬费": [],
    "被抚养人生活费": ["商品房买卖合同", "房地证", "不动产登记证", "居住证明", "村民委员会证明",
                "村委会证明", "营业执照", "结婚证", "劳动合同", "工资银行流水明细",
                "居民身份证", "户口本", "身份信息户籍函", "户口册", "社保缴费记录",
                "土地使用权证", "身份关系证明", "亲属关系证明书", "关系证明", "户口本",
                "身份关系证明", "亲属关系证明书", "关系证明", "出生医学证明"],
    "处理丧葬人员的交通费": ["火车票", "高速费收据", "汽车车票", "汽车票保险单"],
    "处理丧葬人员的误工费": ["农村土地承包经营权证", "鱼池承包合同", "村民委员会证明", "村委会证明",
                   "户口本", "身份信息户籍函", "户口册", "营业执照", "员工入职登记表",
                   "人员名册", "工资流水", "请假证明", "工资表", "劳动合同", "鉴定所鉴定意见书",
                   "鉴定意见书", "鉴定报告", "司法鉴定意见书", "鉴定书", "工资损失证明", "务工损失证明"],
    "精神抚慰金": [],
    "鉴定费": ["鉴定费票据", "鉴定费发票", "发票", "票据"],
    "车辆损失": [],
    "施救费": []
}

PROVINCE_CITY = {"河北": ["石家庄", "唐山", "邯郸", "秦皇岛", "保定", "张家口", "承德", "廊坊", "沧州",
                        "衡水", "邢台", "辛集", "藁城", "晋州", "新乐", "鹿泉", "遵化", "迁安", "武安",
                        "南宫", "沙河", "涿州", "定州", "安国", "高碑店", "泊头", "任丘", "黄骅", "河间",
                        "霸州", "三河", "冀州", "深州"],
                 "山西": ["太原", "大同", "忻州", "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "临汾",
                        "吕梁", "古交", "潞城", "高平", "介休", "永济", "河津", "原平", "侯马", "霍州",
                        "孝义", "汾阳"],
                 "辽宁": ["沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳",
                        "盘锦", "铁岭", "朝阳", "葫芦", "新民", "瓦房店", "普兰", "庄河", "海城", "东港",
                        "凤城", "凌海", "北镇", "大石桥", "盖州", "灯塔", "调兵山", "开原", "凌源",
                        "北票", "兴城"],
                 "吉林": ["长春", "吉林", "四平", "辽源", "通化", "白山", "松原", "白城", "九台",
                        "榆树", "德惠", "舒兰", "桦甸", "蛟河", "磐石", "公主岭", "双辽", "梅河口",
                        "集安", "临江", "大安", "洮南", "延吉", "图们", "敦化", "龙井", "珲春", "和龙"],
                 "黑龙江": ["哈尔滨", "大庆", "齐齐哈尔", "佳木斯", "鸡西", "鹤岗", "双鸭山", "牡丹江",
                         "伊春", "七台河", "黑河", "绥化", "五常", "双城", "尚志", "纳河", "虎林", "密山",
                         "铁力", "同江", "富锦", "绥芬河", "海林", "宁安", "穆林", "北安", "五大连池",
                         "肇东", "海伦", "安达"],
                 "江苏": ["南京", "镇江", "常州", "无锡", "苏州", "徐州", "连云港", "淮安", "盐城", "扬州",
                        "泰州", "南通", "宿迁", "江阴", "宜兴", "邳州", "新沂", "金坛", "溧阳", "常熟",
                        "张家港", "太仓", "昆山", "吴江", "如皋", "通州", "海门", "启东", "东台", "大丰",
                        "高邮", "江都", "仪征", "丹阳", "扬中", "句容", "泰兴", "姜堰", "靖江", "兴化"],
                 "浙江": ["杭州", "嘉兴", "湖州", "宁波", "金华", "温州", "丽水", "绍兴", "衢州", "舟山", "台州",
                        "建德", "富阳", "临安", "余姚", "慈溪", "奉化", "瑞安", "乐清", "海宁", "平湖", "桐乡",
                        "诸暨", "上虞", "嵊州", "兰溪", "义乌", "东阳", "永康", "江山", "临海", "温岭", "龙泉"],
                 "安徽": ["合肥", "蚌埠", "芜湖", "淮南", "亳州", "阜阳", "淮北", "宿州", "滁州", "安庆", "巢湖",
                        "马鞍山", "宣城", "黄山", "池州", "铜陵", "界首", "天长", "明光", "桐城", "宁国"],
                 "福建": ["福州", "厦门", "泉州", "三明", "南平", "漳州", "莆田", "宁德", "龙岩",
                        "福清", "长乐", "永安", "石狮", "晋江", "南安", "龙海", "邵武", "武夷", "建瓯", "建阳",
                        "漳平", "福安", "福鼎"],
                 "江西": ["南昌", "九江", "赣州", "吉安", "鹰潭", "上饶", "萍乡", "景德镇", "新余", "宜春", "抚州",
                        "乐平", "瑞昌", "贵溪", "瑞金", "南康", "井冈山", "丰城", "樟树", "高安", "德兴"],
                 "山东": ["济南", "青岛", "淄博", "枣庄", "东营", "烟台", "潍坊", "济宁", "泰安", "威海", "日照",
                        "莱芜", "临沂", "德州", "聊城", "菏泽", "滨州", "章丘", "胶南", "胶州", "平度", "莱西",
                        "即墨", "滕州", "龙口", "莱阳", "莱州", "招远", "蓬莱", "栖霞", "海阳", "青州", "诸城",
                        "安丘", "高密", "昌邑", "兖州", "曲阜", "邹城", "乳山", "文登", "荣成", "乐陵", "临清",
                        "禹城"],
                 "河南": ["郑州", "洛阳", "开封", "漯河", "安阳", "新乡", "周口", "三门峡", "焦作", "平顶山", "信阳",
                        "南阳", "鹤壁", "濮阳", "许昌", "商丘", "驻马店", "巩义", "新郑", "新密", "登封", "荥阳",
                        "偃师", "汝州", "舞钢", "林州", "卫辉", "辉县", "沁阳", "孟州", "禹州", "长葛", "义马",
                        "灵宝", "邓州", "永城", "项城", "济源"],
                 "湖北": ["武汉", "襄樊", "宜昌", "黄石", "鄂州", "随州", "荆州", "荆门", "十堰",
                        "孝感", "黄冈", "咸宁", "大冶", "丹江口", "洪湖", "石首", "松滋", "宜都",
                        "当阳", "枝江", "老河口", "枣阳", "宜城", "钟祥", "应城", "安陆", "汉川",
                        "麻城", "武穴", "赤壁", "广水", "仙桃", "天门", "潜江", "恩施", "利川"],
                 "湖南": ["长沙", "株洲", "湘潭", "衡阳", "岳阳", "郴州", "永州", "邵阳", "怀化",
                        "常德", "益阳", "张家界", "娄底", "浏阳", "醴陵", "湘乡", "韶山", "耒阳",
                        "常宁", "武冈", "临湘", "汨罗", "津市", "沅江", "资兴", "洪江", "冷水江",
                        "涟源", "吉首"],
                 "广东": ["广州", "深圳", "汕头", "惠州", "珠海", "揭阳", "佛山", "河源", "阳江",
                        "茂名", "湛江", "梅州", "肇庆", "韶关", "潮州", "东莞", "中山", "清远",
                        "江门", "汕尾", "云浮"],
                 "海南": ["海口", "三亚", "琼海", "文昌", "万宁", "五指山", "儋州", "东方"],
                 "四川": ["成都", "绵阳", "德阳", "广元", "自贡", "攀枝花", "乐山", "南充", "内江", "遂宁", "广安",
                        "泸州", "达州", "眉山", "宜宾", "雅安", "资阳", "都江堰", "彭州", "邛崃", "崇州", "广汉",
                        "什邡", "绵竹", "江油", "峨眉山", "阆中", "华蓥", "万源", "简阳", "西昌"],
                 "贵州": ["贵阳", "六盘水", "遵义", "安顺", "清镇", "赤水", "仁怀", "铜仁", "毕节", "兴义", "凯里",
                        "都匀", "福泉"],
                 "云南": ["昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧", "安宁", "宣威", "个旧",
                        "开远", "景洪", "楚雄", "大理", "潞西", "瑞丽"],
                 "陕西": ["西安", "咸阳", "铜川", "延安", "宝鸡", "渭南", "汉中", "安康", "商洛", "榆林",
                        "兴平", "韩城", "华阴"],
                 "甘肃": ["兰州", "天水", "平凉", "酒泉", "嘉峪关", "金昌", "白银", "武威", "张掖", "庆阳",
                        "定西", "陇南", "玉门", "敦煌", "临夏", "合作"],
                 "青海": ["西宁", "格尔木", "德令哈"],
                 "内蒙古": ["呼和浩特", "包头", "乌海", "赤峰", "通辽", "鄂尔多斯", "呼伦贝尔", "巴彦淖尔",
                         "乌兰察布", "霍林郭勒", "满洲里", "牙克石", "扎兰屯", "根河", "额尔古纳", "丰镇",
                         "锡林浩特", "二连浩特", "乌兰浩特", "阿尔山"],
                 "广西": ["南宁", "柳州", "桂林", "梧州", "北海", "崇左", "来宾", "贺州", "玉林", "百色",
                        "河池", "钦州", "防城港", "贵港", "岑溪", "凭祥", "合山", "北流", "宜州", "东兴",
                        "桂平"],
                 "西藏": ["拉萨", "日喀则"],
                 "宁夏": ["银川", "石嘴山", "吴忠", "固原", "中卫", "青铜峡", "灵武"],
                 "新疆": ["乌鲁木齐", "石河子", "阿拉尔市", "图木舒克", "五家渠", "哈密", "吐鲁番", "阿克苏", "喀什",
                        "和田", "伊宁", "塔城", "阿勒泰", "奎屯", "博乐", "昌吉", "阜康", "库尔勒", "阿图什", "乌苏"]}
ORIENTATION = ["华东", "华南", "华北", "中南", "华西", "西南", "东南", "北京", "天津", "重庆", "上海"]

for key in EVIDENCE_KEY_WORDS:
    EVIDENCE_KEY_WORDS[key] = set(EVIDENCE_KEY_WORDS[key])

CN_NUM = {
    u'〇': 0,
    u'一': 1,
    u'二': 2,
    u'三': 3,
    u'四': 4,
    u'五': 5,
    u'六': 6,
    u'七': 7,
    u'八': 8,
    u'九': 9,
    u'零': 0,
    u'壹': 1,
    u'贰': 2,
    u'叁': 3,
    u'肆': 4,
    u'伍': 5,
    u'陆': 6,
    u'柒': 7,
    u'捌': 8,
    u'玖': 9,
    u'貮': 2,
    u'两': 2,
}

CN_UNIT = {
    u'十': 10,
    u'拾': 10,
    u'百': 100,
    u'佰': 100,
    u'千': 1000,
    u'仟': 1000,
    u'万': 10000,
    u'萬': 10000,
    u'亿': 100000000,
    u'億': 100000000,
    u'兆': 1000000000000,
}


def cn2dig(cn):
    """将汉字的数字转换为阿拉伯数字
    :param cn: string
        汉字读数
    :return: int
        转换结果
    """
    try:
        lcn = list(cn)
        unit = 0  # 当前的单位
        ldig = []  # 临时数组
        while lcn:
            cndig = lcn.pop()
            if cndig in CN_UNIT:
                unit = CN_UNIT.get(cndig)
                if unit == 10000:
                    ldig.append('w')  # 标示万位
                    unit = 1
                elif unit == 100000000:
                    ldig.append('y')  # 标示亿位
                    unit = 1
                elif unit == 1000000000000:  # 标示兆位
                    ldig.append('z')
                    unit = 1
                continue
            else:
                dig = CN_NUM.get(cndig)
                if unit:
                    dig = dig * unit
                    unit = 0
                ldig.append(dig)
        if unit == 10:  # 处理10-19的数字
            ldig.append(10)
        ret = 0
        tmp = 0
        while ldig:
            x = ldig.pop()
            if x == 'w':
                tmp *= 10000
                ret += tmp
                tmp = 0
            elif x == 'y':
                tmp *= 100000000
                ret += tmp
                tmp = 0
            elif x == 'z':
                tmp *= 1000000000000
                ret += tmp
                tmp = 0
            else:
                tmp += x
        ret += tmp
        return ret
    except Exception as e:
        print(e)
        print(cn)
        return cn


def split_paragraph(lines):
    """分割文书内容，尽量将同一费用的内容纳入到同一个字符串中
    :param lines: list of string
        文书原始的段落列表
    :return: list of string
        返回分割完成之后的文书内容列表
    """
    doc = []
    newlines = []
    for line in lines:
        if not re.findall("[费金助]：", line) and \
                not re.findall("（[^）]*：[^（]*）", line) and \
                '：' in line:
            newlines.extend(line.split('：'))
        else:
            newlines.append(line)
    for line in newlines:
        # 如果一个段落中包含多个费用的信息，则进行段落拆分，尽量保证一个段落只有一个费用的信息
        if fee_types(line) >= 2:
            if re.findall("；[0-9一二三四五六七八九十]\.[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line) \
                    or re.findall("；[0-9一二三四五六七八九十]、[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line):
                # 消除括号内的分割符干扰
                if re.findall("（[^）]*；[^（]*）", line):
                    for matches in re.findall("（[^）]*；[^（]*）", line):
                        line = line.replace(matches, matches.replace('；', ","))
                contents = re.split(r'；', line)
                doc.extend(contents)
                # 递归检查一下有没有切分干净
                doc = split_paragraph(doc)
            elif re.findall("。[0-9一二三四五六七八九十]\.[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line) \
                    or re.findall("。[0-9一二三四五六七八九十]、[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line):
                if re.findall("（[^）]*。[^（]*）", line):
                    for matches in re.findall("（[^）]*。[^（]*）", line):
                        line = line.replace(matches, matches.replace('。', ","))
                contents = re.split(r'。', line)
                doc.extend(contents)
                doc = split_paragraph(doc)
            elif re.findall("、[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line):
                if re.findall("（[^）]*、[^（]*）", line):
                    for matches in re.findall("（[^）]*、[^（]*）", line):
                        line = line.replace(matches, matches.replace('、', ","))
                contents = re.split(r'、', line)
                doc.extend(contents)
                doc = split_paragraph(doc)
            elif re.findall("；[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line):
                if re.findall("（[^）]*；[^（]*）", line):
                    for matches in re.findall("（[^）]*；[^（]*）", line):
                        line = line.replace(matches, matches.replace('；', ","))
                contents = re.split(r'；', line)
                doc.extend(contents)
                doc = split_paragraph(doc)
            elif re.findall("。[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line):
                if re.findall("（[^）]*。[^（]*）", line):
                    for matches in re.findall("（[^）]*。[^（]*）", line):
                        line = line.replace(matches, matches.replace('。', ","))
                contents = re.split(r'。', line)
                doc.extend(contents)
                doc = split_paragraph(doc)
            # elif re.findall("，[\u4E00-\u9FA5\s]+[费金助].*-?\d+\.?\d*元", line):
            #     contents = re.split(r'，', line)
            #     doc.extend(contents)
            #     doc = split_paragraph(doc)
            else:
                doc.extend(re.split(r'。', line))
        else:
            doc.append(line)
    for i in range(len(doc)):
        if "以上共计" in doc[i]:
            doc[i] = doc[i][:doc[i].index("以上共计")].rstrip('，')
        if "以上合计" in doc[i]:
            doc[i] = doc[i][:doc[i].index("以上合计")].rstrip('，')
        if "共计" in doc[i] and fee_types(doc[i]) > 1:
            doc[i] = doc[i][:doc[i].index("共计")].rstrip('，')
        if re.findall("[^综]合计", doc[i]) and fee_types(doc[i]) > 1:
            doc[i] = doc[i][:doc[i].index("合计")].rstrip('，')
    return doc


def fee_types(line):
    count = 0
    # 检查段落中有多少种费用
    for fee in EVIDENCE_KEY_WORDS.keys():
        if fee in line:
            count += 1
    return count


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


def contains(key_words, line):
    """判断句子line中是否有key_words中的关键词
    :param key_words: list of string
        关键词列表
    :param line: string
        待检查句子
    :return: boolean
        返回判断结果
    """
    for key_word in key_words:
        if key_word in line:
            return True
    return False


def check_money(item, line):
    flag = False
    if "工资" + item in line:
        flag = True
    elif "工资每年" + item in line:
        flag = True
    elif "收入" + item in line:
        flag = True
    elif "收入为" + item in line:
        flag = True
    elif "收入每年" + item in line:
        flag = True
    elif "收入标准" + item in line:
        flag = True
    elif "每天" + item in line:
        flag = True
    elif "每月" + item in line:
        flag = True
    elif "每年" + item in line:
        flag = True
    elif item + '／' in line and not re.findall(item + "(?![／])", line):
        flag = True
    elif item + '/' in line and not re.findall(item + "(?![/])", line):
        flag = True
    return flag


def check_day(candidates, info, row):
    """检查天数合法性
    :param candidates: list of string
        候选天数列表
    :param info: dictionary
        费用信息字典
    :param row: string
        当前段落
    :return: boolean
        返回判断结果
    """
    # 把日期中的日移除掉
    delete_day = []
    for day in candidates:
        if '月' + day in row or "间隔" + day in row:
            delete_day.append(day)
    for day in delete_day:
        while day in candidates:
            candidates.remove(day)
    # 标准是年，则将天数中的365天移除一个
    if "criterion" in info and info["criterion"] and \
            info["criterion"][-1] == "年" and \
            "365天" in candidates:
        candidates.remove("365天")
    info["days"] = candidates
    # 如果找到的天数存在于乘法算式中，则将这个天数认为是正确
    for day in info["days"]:
        if ('×' + day in row) or ('＊' + day in row) or ('*' + day in row):
            info["days"] = [day]
    # 将日的后缀转化为天
    newdays = []
    for day in info["days"]:
        if day.endswith('日'):
            newdays.append(day.replace('日', '天'))
        else:
            newdays.append(day)
    info["days"] = newdays
    # 去除冗余的天数
    if len(info["days"]) == 1 or len(list(set(info["days"]))) == 1:
        info["days"] = [info["days"][0]]
    return info


def check_criterion(info, row):
    """检查标准合法性
    :param info: dictionary
        费用信息字典
    :param row: string
        当前段落
    :return: dictionary
        返回处理完后的费用信息字典
    """
    # 如果找到的标准存在于乘法算式中，则将这个标准认为是正确
    for criterion in re.findall(r'-?\d+\.?\d*元[／/][日天月年]', row):
        if ('×' + criterion in row) or ('＊' + criterion in row) or ('*' + criterion in row):
            info["criterion"] = criterion
    return info


def extract_criterion(info, fee_typ, row):
    """提取费用标准信息
    :param info: dictionary
        费用信息字典
    :param fee_typ: string
        费用名称
    :param row: string
        当前段落
    :return: dictionary
        返回处理好的信息字典
    """
    criterion = re.findall(fee_typ + r'.*-?\d+\.?\d*元[／/][天日月年]', row)
    if (criterion and "criterion" not in info) or \
            (criterion and "criterion" in info and not info["criterion"]):
        info["criterion"] = re.findall(r'-?\d+\.?\d*元[／/][日天月年]', criterion[0])[0]
    criterion = [item for item in re.findall(r'每[日天月年][\u4E00-\u9FA5\s]*-?\d+\.?\d*元', row)
                 if "收入" not in item]
    if (criterion and "criterion" not in info) or \
            (criterion and "criterion" in info and not info["criterion"]):
        info["criterion"] = re.findall(r'每[日天月年][\u4E00-\u9FA5\s]*-?\d+\.?\d*元', criterion[0])[0]
    criterion = re.findall(r'-?\d+\.?\d*元[×]?\d+[日天月年]', row)
    if (criterion and "criterion" not in info) or \
            (criterion and "criterion" in info and not info["criterion"]):
        temp = re.findall(r'-?\d+\.?\d*元[×]?\d+[日天月年]', criterion[0])[0]
        info["criterion"] = temp[:temp.index('元') + 1] + '/' + temp[-1]
    criterion = re.findall(r'-?\d+\.?\d*元÷365', row)
    if (criterion and "criterion" not in info) or \
            (criterion and "criterion" in info and not info["criterion"]):
        temp = re.findall(r'-?\d+\.?\d*元÷365', criterion[0])[0]
        info["criterion"] = temp[:temp.index('元') + 1] + '/年'
    # 后处理标准
    if "criterion" in info and info["criterion"]:
        info = check_criterion(info, row)
    else:
        if re.findall(r"月均收入[为]*\d+\.?\d*元", row):
            temp = re.findall(r"月均收入[为]*\d+\.?\d*元", row)[0]
            info["criterion"] = re.findall(r"\d+\.?\d*元", temp)[0] + '/月'
        else:
            info["criterion"] = ""
    return info


def extract_day(info, fee_typ, row):
    """提取天数信息
    :param info: dictionary
        费用信息字典
    :param fee_typ: string
        费用名称
    :param row: string
        当前段落
    :return: dictionary
        返回处理好的信息字典
    """
    if fee_typ == "交通费":
        if re.findall(r'计[为]?\d+[日天](?![／/])', row):
            days = re.findall(fee_typ + r'.*\d+[日天](?![／/])',
                              re.findall(r'计[为]?\d+[日天](?![／/])', row)[0])
        else:
            days = re.findall(fee_typ + r'.*\d+[日天](?![／/])', row)
    else:
        if re.findall(r'计[为]?\d+[日天](?![／/])', row):
            days = re.findall(fee_typ + r'.*\d+[日天](?![／/])',
                              re.findall(r'计[为]?\d+[日天](?![／/])', row)[0])
            if not days:
                days = re.findall(r'.*\d+[日天](?![／/])',
                                  re.findall(r'计[为]?\d+[日天](?![／/])', row)[0])
        else:
            days = re.findall(fee_typ + r'.{0,3}\d+[日天](?![／/])', row)
    if days and "days" not in info:
        info["days"] = [re.findall(r'\d+[日天](?![／/])', days[0])[0]]
        # 防止是日期中的日
        if '月' + info["days"][0] in row:
            info["days"] = re.findall(r'\d+[天](?![／/])', days[0])
    else:
        temp = re.findall(r'(?![／/])\d+[日天](?![／/])', row)
        if temp:
            info = check_day(temp, info, row)
    return info


def extract_year(info, fee_typ, row):
    """提取年限信息
    :param info: dictionary
        费用信息字典
    :param fee_typ: string
        费用名称
    :param row: string
        当前段落
    :return: dictionary
        返回处理好的信息字典
    """
    if "years" in info and info["years"]:
        return info
    years = re.findall(fee_typ + r'.*\d+年', row)
    if years and "years" not in info:
        for year in years:
            temp_years = re.findall(r'\d+年', year)
            for temp_year in temp_years:
                if int(float(temp_year[:-1])) <= 100:
                    info["years"] = temp_year
                    break
    else:
        info["years"] = ""
    return info


def extract_percent_level(info, row):
    """提取残疾赔偿金中的百分比和伤残等级
    :param info: dictionary
        费用信息字典
    :param row: string
        当前段落
    :return: dictionary
        返回处理好的信息字典
    """
    # 提取出赔付比例百分比
    percent = re.findall(r'残疾赔偿金[^等]*-?\d+\.?\d*[%％]', row)
    if percent and "percent" not in row:
        info["percent"] = list(set(re.findall(r'-?\d+\.?\d*[%％]', row)))
    else:
        info["percent"] = []
    # 提取出伤残等级
    level = re.findall(r'残疾赔偿金.*[0-9一二三四五六七八九十]级', row)
    if level and "disable_level" not in info:
        info["disable_level"] = list(set(re.findall(r'[0-9一二三四五六七八九十]级', row)))
    else:
        info["disable_level"] = []
    return info


def extract_person(info, lines):
    """提取护理人
    :param info: dictionary
        费用信息字典
    :param lines: list of string
        全文句子
    :return: dictionary
        返回处理好的信息字典
    """
    relation_ship = ["父亲", "母亲", "叔叔", "阿姨", "姨父",
                     "哥哥", "嫂子", "弟弟", "弟妹", "姐姐", "姐夫",
                     "儿子", "儿媳", "女儿", "女婿"]
    info["paramedic"] = []
    for line in lines:
        for person in relation_ship:
            if re.findall(f"{person}[\u4E00-\u9FA5、]*护理", line):
                info["paramedic"].append(person)
    info["paramedic"] = list(set(info["paramedic"]))
    return info


def process_basis(s_basis):
    """处理法条格式
    :param s_basis: string
        “《xxx》a条、b条”格式的法条
    :return: 返回 [《xxx》a条,《xxx》b条] 列表格式的法条
        list of string
    """
    s_law = s_basis.split('》')[0].split('《')[1]
    s_law_new = '《' + s_law + '》'
    l_split_law = s_basis.split('、')
    l_res = []
    for x in l_split_law:
        if not x:
            break
        if s_law in x:
            l_res.append(x)
        else:
            l_res.append(s_law_new + x)
    return l_res


def reference(fee, line, typ):
    """提取费用typ的详细信息
    :param fee: dictionary
        相关费用的字典
    :param line: string
        费用的相关段落
    :param typ: string
        费用名称
    :return: dictionary
        返回修正后的费用字典
    """
    # 初始化费用的其他信息
    if "judge_money" in fee and fee["judge_money"]:
        pass
    else:
        fee["judge_money"] = ""
    if "appeal_money" not in fee:
        fee["appeal_money"] = ""
    fee["argued_money"] = ""
    fee["basis"] = []
    fee["evidence"] = []
    fee["argue"] = []
    if ("judge_money" not in fee) or (not line) or (not typ):
        return fee
    # 提取错误时，需要将已经提取到的费用进行清空，后续进行重新提取
    if fee["judge_money"] and check_money(fee["judge_money"], line):
        # 此时提取到的是费用标准
        fee["judge_money"] = ""
    # 如果法院态度出现反转，则重新检查费用
    if check_money(fee["judge_money"], line) or \
       re.findall(r'[本酌][院情][\u4E00-\u9FA5\s]*支持', line) or \
       re.findall(r'[本酌][院情][\u4E00-\u9FA5\s]*保护', line) or \
       re.findall(r'[本酌][院情][\u4E00-\u9FA5\s]*确定', line) or \
       re.findall(r'[^（]本院按照[^）]', line) or \
       re.findall(r'[^（]本院依据[^）]', line) or \
       re.findall(r'[^（]本院酌定[^）]', line) or \
       re.findall(r'[^（]本院认为[^）]', line) or \
       re.findall(r'[^（]本院核[实算][^）]', line) or \
       re.findall(r'[^（]本院确[认定][^）]', line) or \
       ("予以支持" in line) or "主张" in line:
        try:
            if re.findall(r"主张[\u4E00-\u9FA5]*\d+\.?\d*元(?![／/])", line):
                fee["appeal_money"] = re.findall(r"\d+\.?\d*元(?![／/])",
                                                 re.findall(r"主张[\u4E00-\u9FA5]*\d+\.?\d*元(?![／/])", line)[0])[0]
                if check_money(fee["appeal_money"], line):
                    fee["appeal_money"] = ""
            # 抓出句子中的费用(排除工资标准的情况)
            dis = sorted([(abs(line.index(item) - line.index(typ)), item)
                          for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                          if not check_money(item, line)],
                         key=lambda x: x[0])
            if re.findall(f"计\d+\.?\d*元(?![／/])", line):
                fee["judge_money"] = re.findall(f"计\d+\.?\d*元(?![／/])", line)[0][1:]
            elif "本院按照" in line:
                # 法院态度出现反转时选择离“本院按照”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index("本院按照"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index("本院按照") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif "本院依据" in line:
                # 法院态度出现反转时选择离“本院依据”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index("本院依据"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index("本院依据") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif "本院酌定" in line:
                # 法院态度出现反转时选择离“本院酌定”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index("本院酌定"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index("本院酌定") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif "本院认为" in line:
                # 法院态度出现反转时选择离“本院认为”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index("本院认为"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index("本院认为") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif "本院核" in line:
                # 法院态度出现反转时选择离“本院核实/算”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index("本院核"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index("本院核") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif re.findall(r'[^（]本院确[认定][^）]', line):
                # 法院态度出现反转时选择离“本院确认/定”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index("本院确"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index("本院确") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif re.findall(r'[本酌][院情][\u4E00-\u9FA5\s]*支持', line) and \
                    "本院予以支持" not in line:
                # 法院态度出现反转时选择离“支持”最近的
                pre = "酌情" if "酌情支持" in line else ""
                fee["judge_money"] = sorted([(line.index(item) - line.index(pre + "支持"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index(pre + "支持") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif re.findall(r'[本酌]*[院情]*[\u4E00-\u9FA5\s]*保护', line):
                pre = "酌情" if "酌情保护" in line else ""
                # 法院态度出现反转时选择离“保护”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index(pre + "保护"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index(pre + "保护") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif re.findall(r'[本酌]*[院情]*[\u4E00-\u9FA5\s]*确定', line):
                pre = "酌情" if "酌情确定" in line else ""
                # 法院态度出现反转时选择离“确定”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index(pre + "确定"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index(pre + "确定") >= 0)],
                                            key=lambda x: x[0])[0][1]
            elif "予以支持" in line:
                # 法院态度出现反转时选择离“予以支持”最近的
                fee["judge_money"] = sorted([(line.index(item) - line.index("予以支持"), item)
                                             for item in re.findall(r'\d+\.?\d*元(?![／/])', line)
                                             if not check_money(item, line) and
                                             (line.index(item) - line.index("予以支持") <= 0)],
                                            key=lambda x: x[0])[0][1]
                fee["appeal_money"] = fee["judge_money"]
            elif fee["judge_money"] and check_money(fee["judge_money"], line):
                # 防止提取到的是费用标准
                temp_line = line.replace(fee["judge_money"], '')
                fee["judge_money"] = re.findall(r'\d+\.?\d*元(?![／/])', temp_line)[0]
                fee["appeal_money"] = fee["judge_money"]
            else:
                fee["judge_money"] = dis[0][1]
                fee["appeal_money"] = fee["judge_money"]
        except Exception as e:
            print(e)
            print(line)
    with open("evidence.txt", encoding="utf-8") as f:
        for item in f.readlines():
            if item.strip() in line and item.strip() != "证明":
                fee["evidence"].append(item.strip())
    temp = re.findall(r'《[\u4E00-\u9FA5\s]+》[\u4E00-\u9FA5\s、]*条', line)
    fee["cause"] = line
    # 提取相关法条
    if temp:
        for item in temp:
            fee["basis"].extend(item.split('，'))
        law_items = []
        for item in fee["basis"]:
            law_items.extend(process_basis(item))
        fee["basis"] = law_items
    fee["argue"] = [item for item in re.split(r"[，。；、]", line) if re.findall(r"(?:辩称|抗辩|过长|过高)", item)]
    if fee["argue"] and re.findall(r"不[\u4E00-\u9FA5]承担", fee["argue"][0]):
        fee["argued_money"] = "0元"
    return fee


def get_medical(lines):
    """提取文档中医疗费的总金额
    :param lines: list of string
        文档对象
    :return: dict
        字典，存放医疗费的总金额
    """
    info = dict()
    info = get_appeal_money(info, lines, "医疗费")
    info = get_appeal_money(info, lines, "医药费")
    info = get_appeal_money(info, lines, "医疗赔偿金")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "医疗赔偿金" in line:
            line = line.replace("医疗赔偿金", "医疗费")
        if "医药费" in line:
            line = line.replace("医药费", "医疗费")
        if "医疗费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            # 先去除数字间的逗号
            line = replace_commas(line)
            # 防止有括号中的子费用干扰
            line = re.sub(u"（.*?）", "", line)
            temp = re.findall(r'医疗费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "医疗费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                # 防止费用是汉字
                temp = re.findall(r'医疗费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            fee = re.findall(r'医疗费[^等]*-?\d+\.?\d*元', line)
            # 从该句子中提取出数字
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "医疗费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_mess(lines):
    """提取文档中伙食补助信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，伙食补助信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "住院伙食补助费")
    info = get_appeal_money(info, lines, "住院伙食补助")
    info = get_appeal_money(info, lines, "伙食补助费")
    info = get_appeal_money(info, lines, "伙食补助")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "住院伙食补助" in line:
            line = line.replace("住院伙食补助", "伙食补助")
        if "伙食补助" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'伙食补助[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "伙食补助")
                info = extract_criterion(info, "伙食补助", line)
                info = extract_day(info, "伙食补助", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'伙食补助[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取出费用标准
            info = extract_criterion(info, "伙食补助", line)
            # 提取出住院天数
            info = extract_day(info, "伙食补助", line)
            # 提取总花费
            fee = re.findall(r'伙食补助[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "伙食补助")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_nutrition(lines):
    """提取文档中的营养费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，营养费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "营养费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "营养费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'营养费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "营养费")
                info = extract_criterion(info, "营养费", line)
                info = extract_day(info, "营养期", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'营养费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取出费用标准
            info = extract_criterion(info, "营养费", line)
            # 提取出住院天数
            info = extract_day(info, "营养期", line)
            # 提取总花费
            fee = re.findall(r'营养费[^等]*-?\d+\.?\d*元', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "营养费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_post_cure(lines):
    """提取文档中的后期治疗费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，后期治疗费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "后续治疗费")
    info = get_appeal_money(info, lines, "后期治疗费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "后续治疗费" in line:
            line = line.replace("后续治疗费", "后期治疗费")
        if "后期治疗费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'后期治疗费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "后期治疗费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'后期治疗费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取总花费
            fee = re.findall(r'后期治疗费[^等]*-?\d+\.?\d*元', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "后期治疗费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_nurse(lines):
    """提取文档中的护理费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，护理费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "护理费")
    info = get_appeal_money(info, lines, "陪护费")
    lines = split_paragraph(lines)
    info = extract_person(info, lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "护工" in line:
            line = line.replace("护工", "护理费")
        if "护理费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'护理费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "护理费")
                info = extract_criterion(info, "护理费", line)
                info = extract_day(info, "护理期", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'护理费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取出费用标准
            info = extract_criterion(info, "护理费", line)
            # 提取出住院天数
            info = extract_day(info, "护理期", line)
            # 提取总花费
            fee = re.findall(r'护理费[^等]*-?\d+\.?\d*元', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "护理费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_loss_working(lines):
    """提取文档中的误工信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，误工损失信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "误工费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "误工费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'误工费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "误工费")
                info = extract_criterion(info, "误工费", line)
                info = extract_day(info, "误工期", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'误工费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取出费用标准
            info = extract_criterion(info, "误工费", line)
            # 提取出误工天数
            info = extract_day(info, "误工期", line)
            # 提取总花费
            fee = re.findall(r'费.*\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "误工费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_traffic(lines):
    """提取文档中的交通费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，交通费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "交通费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "交通费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'交通费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "交通费")
                info = extract_criterion(info, "交通费", line)
                info = extract_day(info, "交通费", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'交通费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取出费用标准
            info = extract_criterion(info, "交通费", line)
            # 提取出天数
            info = extract_day(info, "交通费", line)
            # 提取总花费
            fee = re.findall(r'交通费[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "交通费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_disable(lines):
    """提取文档中的残疾赔偿金信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，残疾赔偿金信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "残疾赔偿金")
    info = get_appeal_money(info, lines, "伤残赔偿金")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "伤残赔偿金" in line:
            line = line.replace("伤残赔偿金", "残疾赔偿金")
        if "残疾赔偿金" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'残疾赔偿金[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "残疾赔偿金")
                info = extract_criterion(info, "残疾赔偿金", line)
                info = extract_year(info, "残疾赔偿金", line)
                info = extract_percent_level(info, line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'残疾赔偿金[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取出费用标准
            info = extract_criterion(info, "残疾赔偿金", line)
            # 提取出年限
            info = extract_year(info, "残疾赔偿金", line)
            # 提取出赔付比例百分比及伤残等级
            info = extract_percent_level(info, line)
            # 提取总金额
            fee = re.findall(r'残疾赔偿金[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "残疾赔偿金")
                info = extract_criterion(info, "残疾赔偿金", line)
                info = extract_year(info, "残疾赔偿金", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                else:
                    break
    else:
        info = reference(info, "", "")
    return info


def get_death(lines):
    """提取文档中的残疾赔偿金信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，死亡赔偿金信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "死亡赔偿金")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "死亡赔偿金" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'死亡赔偿金[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "死亡赔偿金")
                info = extract_year(info, "死亡赔偿金", line)
                info = extract_criterion(info, "死亡赔偿金", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'死亡赔偿金[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取出费用标准
            info = extract_criterion(info, "死亡赔偿金", line)
            # 提取出年限
            info = extract_year(info, "死亡赔偿金", line)
            # 提取总金额
            fee = re.findall(r'死亡赔偿金[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "死亡赔偿金")
                info = extract_criterion(info, "死亡赔偿金", line)
                info = extract_year(info, "死亡赔偿金", line)
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_bury(lines):
    """提取文档中的丧葬费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，丧葬费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "丧葬费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "丧葬费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'丧葬费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "丧葬费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'丧葬费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取总金额
            fee = re.findall(r'丧葬费[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "丧葬费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_life(lines):
    """提取文档中的被抚养人生活费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，被抚养人生活费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "被抚养人生活费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "被抚养人生活费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'被抚养人生活费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "被抚养人生活费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'被抚养人生活费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取总金额
            fee = re.findall(r'被抚养人生活费[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "被抚养人生活费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_mind(lines):
    """提取文档中的精神抚慰金信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，精神抚慰金信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "精神抚慰金")
    info = get_appeal_money(info, lines, "精神损害抚慰金")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "精神损害抚慰金" in line:
            line = line.replace("精神损害抚慰金", "精神抚慰金")
        if "精神抚慰金" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'精神抚慰金[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "精神抚慰金")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'精神抚慰金[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取总金额
            fee = re.findall(r'精神抚慰金[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "精神抚慰金")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_traffic_for_process_bury(lines):
    """提取文档中的处理丧葬人员的交通费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，处理丧葬人员的交通费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "处理事故及办理丧葬事宜人员交通费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if flag:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'处理事故及办理丧葬事宜人员交通费[^等]*-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "处理事故及办理丧葬事宜人员交通费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'处理事故及办理丧葬事宜人员交通费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取总金额
            fee = re.findall(r'处理.*丧葬.*人员.*交通费[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                line = re.sub("处理.*丧葬.*人员.*交通费", "处理丧葬人员的交通费", line)
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "处理丧葬人员的交通费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_loss_working_for_process_bury(lines):
    """提取文档中的处理丧葬人员的误工费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，处理丧葬人员的误工费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "处理丧葬人员的误工费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if flag:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'处理丧葬人员的误工费[^等]*-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "处理丧葬人员的误工费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'处理丧葬人员的误工费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取总金额
            fee = re.findall(r'处理.*丧葬.*人员.*误工费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "处理丧葬人员的误工费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_appraise(lines):
    """提取文档中的鉴定费信息
    :param lines: list of string
        文档对象
    :return: dict
        字典，鉴定费信息
    """
    info = dict()
    info = get_appeal_money(info, lines, "鉴定费")
    info = get_appeal_money(info, lines, "鉴定检查费")
    info = get_appeal_money(info, lines, "评估费")
    lines = split_paragraph(lines)
    flag = False
    for line in lines:
        if not line:
            continue
        if "本院认为" in line or "本院认定" in line:
            flag = True
        if "鉴定检查费" in line:
            line = line.replace("鉴定检查费", "鉴定费")
        if "评估费" in line:
            line = line.replace("评估费", "鉴定费")
        if "鉴定费" in line and flag and '元' in line:
            if fee_types(line) >= 2:
                continue
            line = replace_commas(line)
            temp = re.findall(r'鉴定费[^等]{0,3}-?\d+\.?\d*元(?![／/])', line)
            if temp:
                info["judge_money"] = re.findall(r'-?\d+\.?\d*元(?![／/])', temp[0])[0]
                info = reference(info, line, "鉴定费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
            else:
                temp = re.findall(r'鉴定费[\u4E00-\u9FA5\s]+元', line)
                if temp:
                    start = 0
                    for i in range(len(temp[0])):
                        if temp[0][start] not in set(list(CN_NUM.keys()) + list(CN_UNIT.keys())):
                            start += 1
                        else:
                            break
                    chinese_num = temp[0][start:temp[0].index("元")]
                    num = cn2dig(chinese_num)
                    line = line.replace(chinese_num, str(num))
            # 提取总金额
            fee = re.findall(r'鉴定费[^等]*-?\d+\.?\d*元(?![／/])', line)
            if fee and "judge_money" not in info:
                money_list = [money for money in re.findall(r'-?\d+\.?\d*元(?![／/])', fee[0])
                              if not check_money(money, fee[0])]
                info["judge_money"] = money_list[0] if len(money_list) >= 1 else ""
                info = reference(info, line, "鉴定费")
                # 检查总金额，如果不合法，则本次搜索无效
                if "judge_money" in info and check_money(info["judge_money"], line):
                    info = {}
                    continue
                break
    else:
        info = reference(info, "", "")
    return info


def get_total_loss(doc):
    """提取文档中的损失合计
    :param doc: list of string
        文档对象
    :return: dict
        字典，损失合计信息
    """
    lines = list(doc)
    info = dict()
    info["judge_money"] = ""
    flag, judge_idx = False, 0
    for i in range(len(lines)):
        if re.findall(r"^[综以]上", lines[i]) or re.findall("(?:本院认为|判决如下)", lines[i]):
            flag = True
            if re.findall(r"[如下]*判决(?:主文)?[如下：]+", lines[i]):
                judge_idx = i if judge_idx == 0 else judge_idx
        if re.findall(r"[如下]*(?:诉讼请求|诉称)[如下：]*", lines[i]):
            flag = False
        if not lines[i] or not flag:
            continue
        if fee_types(lines[i]) <= 1:    # 这一行只是在描述某一项费用，跳过
            continue
        row = replace_commas(lines[i])
        for line in re.split(r"[、，。；【】]", row):
            if fee_types(line):    # 是某一项费用的合计时跳过
                continue
            if re.findall("[各项]*[\u4E00-\u9FA5]*计[为人民币款]*\d+\.?\d*元(?![／/])", line) and '元' in line:
                if re.findall(r"(?:受理费|诉讼费|减半)", row):
                    continue
                temp = re.findall("[各项]*[\u4E00-\u9FA5]*计[为人民币款]*\d+\.?\d*元(?![／/])", line)[0]
                info["judge_money"] = re.findall("\d+\.?\d*元(?![／/])", temp)[0]
            elif re.findall("[损失]+\d+\.?\d*元(?![／/])", line) and '元' in line:
                temp = re.findall("[损失]+\d+\.?\d*元(?![／/])", line)[0]
                info["judge_money"] = re.findall("\d+\.?\d*元(?![／/])", temp)[0]
            if info["judge_money"] and info["judge_money"] != "0元":
                break
    # 防止判决金额明细另起一行，每行一项费用，需要从“判决如下”的下一行继续检查
    if judge_idx:
        money = []
        for i in range(judge_idx + 1, len(lines)):
            # 去除数字中的逗号
            lines[i] = replace_commas(lines[i])
            # 去除括号中的明细
            if re.findall(r"[(（].*[）)]", lines[i]):
                lines[i] = re.sub(r"[(（][^（）()]+[）)]", '', lines[i])
            if re.findall(r"［.*］", lines[i]):
                lines[i] = re.sub(r"［.*］", '', lines[i])
            if re.findall(r"第[一二三四五六七八九十0-9]+项", lines[i]):
                continue
            if re.findall(r'《[\u4E00-\u9FA5\s]+》[\u4E00-\u9FA5\s、]*条', lines[i]) or re.findall(r"(?:受理费|诉讼费|减半)", lines[i]):
                # 到了法条行和受理费行就退出循环
                break
            if re.findall("[各项]*[\u4E00-\u9FA5]*[合共计][为人民币款]*\d+\.?\d*元(?![／/])", lines[i]):
                temp = re.findall("[各项]*[\u4E00-\u9FA5]*[合共计][为人民币款]*\d+\.?\d*元(?![／/])", lines[i])[-1]
                if re.findall(r"再赔[\u4E00-\u9FA5]*\d+\.?\d*元", lines[i]):    # 再赔表示已经有部分赔付，优先级最高
                    content = re.findall(r"再赔[\u4E00-\u9FA5]*\d+\.?\d*元", lines[i])[0]
                    money.append(round(float(re.findall(r"\d+\.?\d*元", content)[0][:-1])))
                elif re.findall(r"(?:实际|还应)支付[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i]):
                    content = re.findall(r"(?:实际|还应)支付[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i])[0]
                    money.append(float(re.findall(r"\d+\.?\d*元", content)[0][:-1]))
                else:
                    money.append(float(re.findall("\d+\.?\d*元(?![／/])", temp)[0][:-1]))
            elif re.findall(r"[各项经济]*(?:上述|合共|合计|共计|共|计|[应再]赔|损失)[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i]):
                temp = re.findall(r"[各项经济]*(?:上述|合共|合计|共计|共|计|[应再]赔|损失)[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i])
                if re.findall(r"再赔[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i]):
                    content = re.findall(r"再赔[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i])[0]
                    money.append(float(re.findall(r"\d+\.?\d*元", content)[0][:-1]))
                elif re.findall(r"(?:实际|还应)支付[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i]):
                    content = re.findall(r"(?:实际|还应)支付[\u4E00-\u9FA5]*[人民币]*\d+\.?\d*元", lines[i])[0]
                    money.append(float(re.findall(r"\d+\.?\d*元", content)[0][:-1]))
                else:
                    money.append(round(sum(list(set([float(re.findall(r"\d+\.?\d*元", content)[0][:-1])
                                                     for content in temp]))), 2))
            elif re.findall("[各项经济的]+损失[人民币]*\d+\.?\d*元(?![／/])", lines[i]):
                temp = re.findall("[各项经济的]+损失[人民币]*\d+\.?\d*元(?![／/])", lines[i])[0]
                money.append(float(re.findall("\d+\.?\d*元(?![／/])", temp)[0][:-1]))
            elif re.findall("\d+\.?\d*元(?![／/])", lines[i]):
                if re.findall(r"(?:返还|退还)", lines[i]):
                    continue
                money.append(sum(list(set([float(re.findall(r"\d+\.?\d*", item)[0])
                                           for item in re.findall("[费用助金失为至近][人民币]*\d+\.?\d*元(?![／/])", lines[i])]))))
        if money:
            info["judge_money"] = f"{round(sum(money), 2)}元"
    return info


def get_appeal_money(fee, doc, typ):
    if "appeal" in fee and "appeal_money" in fee:
        return fee
    fee["appeal"] = ""
    lines = list(doc)
    for i in range(len(lines)):
        # 去除数字中的逗号
        lines[i] = replace_commas(lines[i])
        # 去除括号中的明细
        if re.findall(r"（.*）", lines[i]):
            lines[i] = re.sub(r"（[^（）]+）", '', lines[i])
        if re.findall(r"\d+\.?\d*万", lines[i]):  # 把万转成对应数字
            for item in re.findall(r"\d+\.?\d*万", lines[i]):
                lines[i] = lines[i].replace(item, str(round(float(re.findall(r"\d+\.?\d*", item)[0]) * 10000, 2)))
        if re.findall(r"[如下]*(?:诉讼请求|诉称|请求判令)[如下：]*", lines[i]):
            raw_line = lines[i]
            if "变更" in lines[i]:
                lines[i] = lines[i].split("变更")[-1]
            elif "增加" in lines[i]:
                lines[i] = lines[i].split("增加")[-1]
            if re.findall(r"事实[与和及]理由", lines[i]):
                lines[i] = re.split(r"事实[与和及]理由", lines[i])[0]
            if not fee["appeal"]:
                fee["appeal"] = raw_line.split("：")[-1]
            if re.findall(f"{typ}\d+\.?\d*元", lines[i]):
                fee["appeal"] = raw_line.split("：")[-1]
                fee["appeal_money"] = re.findall(r"\d+\.?\d*元", re.findall(f"{typ}\d+\.?\d*元", lines[i])[0])[0]
                break
    return fee


def get_appeal(doc):
    """提取文书中原告的诉求金额"""
    lines = list(doc)
    info = dict()
    info["appeal_money"] = ""
    flag = 0
    for i in range(len(lines)):
        if re.findall(r"[如下]*(?:诉讼请求|诉称|请求判令)[如下：]*", lines[i]):
            flag = i
        # 去除数字中的逗号
        lines[i] = replace_commas(lines[i])
        # 去除括号中的明细
        if re.findall(r"（.*）", lines[i]):
            lines[i] = re.sub(r"（[^（）]+）", '', lines[i])
        if re.findall(r"\d+\.?\d*万", lines[i]):      # 把万转成对应数字
            for item in re.findall(r"\d+\.?\d*万", lines[i]):
                lines[i] = lines[i].replace(item, str(round(float(re.findall(r"\d+\.?\d*", item)[0])*10000, 2)))
        if re.findall(r"[如下]*(?:诉讼请求|诉称|请求判令)[如下：]*", lines[i]):
            if "变更" in lines[i]:
                lines[i] = lines[i].split("变更")[-1]
            elif "增加" in lines[i]:
                lines[i] = lines[i].split("增加")[-1]
            if re.findall(r"事实[与和及]理由", lines[i]):
                lines[i] = re.split(r"事实[与和及]理由", lines[i])[0]
            if re.findall(r"(?:各项|各种|经济)[损失共计费用为]+[人民币款]*\d+\.?\d*元", lines[i]):
                content = re.findall(r"(?:各项|各种|经济)[损失共计费用为]+[人民币款]*\d+\.?\d*元", lines[i])[0]
                info["appeal_money"] = re.findall(r"\d+\.?\d*元", content)[0]
            elif re.findall(r"(?:计|等|原告)[人民币款]*\d+\.?\d*元", lines[i]):
                content = re.findall(r"(?:计|等|原告)[人民币款]*\d+\.?\d*元", lines[i])[0]
                info["appeal_money"] = re.findall(r"\d+\.?\d*元", content)[0]
            elif re.findall(r"\d+\.?\d*元(?![／/])", lines[i]):
                # 一般来说不会有两个费用完全相同，去个重
                info["appeal_money"] = str(round(sum(list(set([float(re.findall(r"\d+\.?\d*", item)[-1])
                                                               for item in re.findall(r"[费用助金失为至近][人民币]*\d+\.?\d*元(?![／/])", lines[i])]))), 2)).rstrip('0') + "元"
            if info["appeal_money"] and info["appeal_money"] != "0元":
                break
    # 防止诉讼的费用明细另起一行，每行一项费用
    if flag and re.findall(r"^[0-9一二三四五六七八九十]+", lines[flag + 1]) and not re.findall(r"^[0-9一二三四五六七八九十]+", lines[flag]):
        money = []
        for i in range(flag + 1, len(lines)):
            lines[i] = replace_commas(lines[i])
            if not re.findall(r"^[0-9一二三四五六七八九十]+", lines[i]):
                break
            elif re.findall("\d+\.?\d*元(?![／/])", lines[i]):
                money.append(round(sum(list(set([float(re.findall(r"\d+\.?\d*", item)[0])
                                                 for item in re.findall("\d+\.?\d*元(?![／/])", lines[i])]))), 2))
        if money:
            info["appeal_money"] = f"{round(sum(list(set(money))), 2)}元"
    if info["appeal_money"] == "元":
        info["appeal_money"] = ""
    return info


def get_appraise_info(lines):
    """提取文书中的鉴定信息"""
    def check_office(item):
        if not re.findall(r"(?:所|中心|部门|估有限公司)", item) or item.startswith('被'):
            item = ""     # 将不符合要求的鉴定所无效化
        return item
    info = dict()
    info["appraising_office"] = ""
    info["appraising_id"] = ""
    info["appraising_content"] = ""
    info["appraising_level"] = ""
    for line in lines:
        # 鉴定所名称
        if not info["appraising_office"]:
            if re.findall(r'经?委托[\u4E00-\u9FA5。；，：“”（）、？《》]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line):
                office = re.findall(r'经?委托[\u4E00-\u9FA5。；，：“”（）、？《》]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line)[0]
                info["appraising_office"] = re.sub(r"[。；，：“”（）、？《》]", "", office[3:] if office[0] == '经' else office[2:])
                if info["appraising_office"][0] in "的后由":
                    info["appraising_office"] = info["appraising_office"][1:]
            elif re.findall(r'经?委托[\u4E00-\u9FA5]+[司法医学]*鉴定[所中心]*', line):
                office = re.findall(r'经?委托[\u4E00-\u9FA5]+[司法医学]*鉴定[所中心]*', line)[0]
                info["appraising_office"] = office[3:] if office[0] == '经' else office[2:]
            info["appraising_office"] = check_office(info["appraising_office"])
            if not info["appraising_office"] and re.findall(r'日?经[\u4E00-\u9FA5]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line):
                office = re.findall(r'日?经[\u4E00-\u9FA5]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line)[0]
                info["appraising_office"] = office[2:] if office[0] == '日' else office[1:]
            info["appraising_office"] = check_office(info["appraising_office"])
            if not info["appraising_office"] and re.findall(r'日[\u4E00-\u9FA5]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line):
                office = re.findall(r'日[\u4E00-\u9FA5]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line)[0]
                info["appraising_office"] = office[1:]
            info["appraising_office"] = check_office(info["appraising_office"])
            if not info["appraising_office"] and re.findall(r'[，、][\u4E00-\u9FA5]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line):
                office = re.findall(r'[，、][\u4E00-\u9FA5]+[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line)[0][1:]
                info["appraising_office"] = office[4:] if office.startswith("本院确认") else office
            info["appraising_office"] = check_office(info["appraising_office"])
            if not info["appraising_office"] and re.findall(r'^[\u4E00-\u9FA5]{2,6}[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line):
                info["appraising_office"] = re.findall(r'^[\u4E00-\u9FA5]{2,6}[司法医学]*鉴定(?:所|中心|部门|评估有限公司)', line)[0]
            info["appraising_office"] = check_office(info["appraising_office"])
            if not info["appraising_office"] and re.findall(r"鉴定(?:所|中心|部门|评估有限公司)：", line):
                info["appraising_office"] = line.split('：')[1]
            info["appraising_office"] = check_office(info["appraising_office"])
            if not info["appraising_office"] and re.findall(r'经[\u4E00-\u9FA5]+(?:鉴定所|鉴定中心|鉴定部门|估有限公司)', line):
                office = re.findall(r'经[\u4E00-\u9FA5]+(?:鉴定所|鉴定中心|鉴定部门|估有限公司)', line)[0]
                info["appraising_office"] = office[1:]
            info["appraising_office"] = check_office(info["appraising_office"])
        # 鉴定书编号
        if re.findall(r'[司法鉴定所中心]*[【〔（\[]\d+[】）〕\]][道临交]鉴字第?[-a-zA-Z\d]+号?', line):
            info["appraising_id"] = list(set(re.findall(r'[司法鉴定所中心]*[【〔（\[]\d+[】）〕\]][道临交]鉴字第?[-a-zA-Z\d]+号?', line)))
        elif re.findall(r'鉴通字[【〔（\[]\d+[】）〕\]]第?[-a-zA-Z\d]+号?', line):
            info["appraising_id"] = list(set(re.findall(r'鉴通字[【〔（\[]\d+[】）〕\]]第?[-a-zA-Z\d]+号?', line)))
        # 鉴定内容
        if "鉴定" in line:
            if "鉴定意见为：" in line:
                info["appraising_content"] = line.split('鉴定意见为：')[-1]
            elif "意见为：" in line:
                info["appraising_content"] = line.split('意见为：')[-1]
            elif re.findall(r"意见称[：，]", line):
                info["appraising_content"] = re.split(r'意见称[：，]', line)[-1]
            elif "鉴定意见如下：" in line:
                info["appraising_content"] = line.split('鉴定意见如下：')[-1]
            elif re.findall(r"^[本院]认为：", line):
                info["appraising_content"] = line.split('认为：')[-1]
            elif "鉴定：" in line:
                info["appraising_content"] = line.split('鉴定：')[-1]
            elif "鉴定为" in line:
                info["appraising_content"] = line.split('鉴定为')[-1]
            elif "鉴定意见：" in line:
                info["appraising_content"] = line.split('鉴定意见：')[-1]
            elif "结论：" in line:
                info["appraising_content"] = line.split('结论：')[-1]
            elif "结论为：" in line:
                info["appraising_content"] = line.split('结论为：')[-1]
            elif "结论如下：" in line:
                info["appraising_content"] = line.split('结论如下：')[-1]
            elif "明确：" in line and not info["appraising_content"]:
                info["appraising_content"] = line.split("明确：")[-1]
            elif "鉴定意见为" in line:
                info["appraising_content"] = line.split("鉴定意见为")[-1]
            elif "意见为" in line:
                info["appraising_content"] = line.split('意见为')[-1]
            elif "鉴定所鉴定" in line and not info["appraising_content"]:
                info["appraising_content"] = line.split("鉴定所鉴定")[-1]
            elif "鉴定，" in line and not info["appraising_content"]:
                info["appraising_content"] = line.split("鉴定，")[-1]
            elif "载明，" in line:
                info["appraising_content"] = line.split("载明，")[-1]
            elif "鉴定原告" in line:
                info["appraising_content"] = line.split("鉴定原告")[-1]
        # 为了防止鉴定内容过长，在没有对鉴定内容编号划分的情况下只取第一句话
        if info["appraising_content"] and (not re.findall(r"[0-9一二三四五六七八九十][、.]", info["appraising_content"]) or len(info["appraising_content"]) > 50):
            info["appraising_content"] = info["appraising_content"].split('。')[0]
        # 鉴定等级
        info["appraising_content"] = re.sub(r"（[^（）]+）", '', info["appraising_content"])
        line = re.sub(r"（[^（）]+）", '', line)
        if re.findall(r'[0-9一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾]+级', info["appraising_content"]):
            info["appraising_level"] = list(set(re.findall(r'[0-9一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾]+级', info["appraising_content"])))
        elif re.findall(r'[0-9一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾]+级', line):
            info["appraising_level"] = list(set(re.findall(r'[0-9一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾]+级', line)))
            if info["appraising_content"] and "不构成伤残" in info["appraising_content"]:
                info["appraising_level"] = ""
        if not info["appraising_content"] and info["appraising_level"]:
            info["appraising_content"] = '、'.join(info["appraising_level"]).rstrip('、') + "伤残"
        info["appraising_content"] = info["appraising_content"].strip('，')
    info["appraising_office"] = find_office(info["appraising_office"])
    return info


def get_acceptance(lines):
    """提取文书中的受理费信息"""
    info = dict()
    info["judge_money"] = ""
    for line in lines[::-1]:
        # 先去除数字间的逗号
        line = replace_commas(line)
        if re.findall(r"(?:受理费|受理|诉讼费)", line):
            if info["judge_money"]:
                break
            if re.findall(r"受理[费]?[\u4E00-\u9FA5]+\d+\.?\d*元", line):
                content = re.findall(r"受理[费]?[\u4E00-\u9FA5]+\d+\.?\d*元", line)[0]
                if not re.findall(r"受理[费]?减半[\u4E00-\u9FA5]+\d+\.?\d*元", line):
                    info["judge_money"] = re.findall(r"\d+\.?\d*元", content)[0]
            elif re.findall(r"诉讼费[^共][\u4E00-\u9FA5]+\d+\.?\d*元", line):
                content = re.findall(r"诉讼费[^共][\u4E00-\u9FA5]+\d+\.?\d*元", line)[0]
                if not re.findall(r"诉讼费减半[\u4E00-\u9FA5]+\d+\.?\d*元", line):
                    info["judge_money"] = re.findall(r"\d+\.?\d*元", content)[0]
            if not info["judge_money"] and re.findall(r"减半[收取为人民币计]+\d+\.?\d*元", line):
                content = re.findall(r"减半[收取为人民币计]+\d+\.?\d*元", line)[0]
                money = float(re.findall(r'\d+\.?\d*元', content)[0][:-1]) * 2
                info["judge_money"] = f"{money}元"
    return info


def get_non_medical_insurance(lines):
    """提取包含非医保用药的上下文"""
    contents = []
    for line in lines:
        if re.findall(r"非[医社]保[用药]*", line):
            contents = [sentence for sentence in line.split('。') if re.findall(r"非[医社]保[用药]*", sentence)]
    return {"context": contents}


def get_franchise(lines):
    """提取免赔"""
    contents = []
    for line in lines:
        contents = [sentence for sentence in line.split('。')
                    if "免责" in sentence or "责任免除" in sentence]
    return {"context": contents}


def get_discount_rate(info):
    """提取扣减率"""
    info["discount_rate"] = ""
    if info.get("fee_appeal", {}).get("appeal_money") and info.get("fee_total_loss", {}).get("judge_money"):
        appeal = float(info["fee_appeal"]["appeal_money"][:-1])
        total_loss = float(info["fee_total_loss"]["judge_money"][:-1])
        if appeal:
            info["discount_rate"] = f"{round((appeal - total_loss) * 100 / appeal, 2)}%"
    return info


def get_legal_provision(lines):
    """提取文书中的所有法条"""
    legal_provision = []
    for line in lines:
        temp = re.findall(r'《[\u4E00-\u9FA5\s]+》[\u4E00-\u9FA5\s、]*条', line)
        # 提取相关法条
        if temp:
            for item in temp:
                legal_provision.extend(item.split('，'))
            law_items = []
            for item in legal_provision:
                law_items.extend(process_basis(item))
            legal_provision = law_items
    return sorted(list(set(legal_provision)))


def find_office(office):
    office = office.strip('，')
    office = office.strip("鉴定")
    office = office.strip("结合")
    for word in ["委托", "指定", "选定", "申请", "确定", "提供", "根据", "评定",
                 "由", "在", "了", "的", "为"]:
        office = office.split(word)[-1]
    for enum in ["鉴定所", "鉴定中心", "鉴定部门", "估有限公司"]:
        idx = office.find(enum)
        if idx > 0:
            office = office[:idx + len(enum)]
    for pos in ORIENTATION:
        idx = office.find(pos)
        if idx > 0:
            office = office[idx:]
    for province in PROVINCE_CITY.keys():
        idx = office.find(province)
        if idx > 0:
            office = office[idx:]
    for cities in PROVINCE_CITY.values():
        for city in cities:
            if city == "津市" and "天津" in office:
                pass
            else:
                idx = office.find(city)
            if idx > 0:
                office = office[idx:]
    office = office.split("对")[-1]
    office = office.split("到")[-1]
    return office


def get_province(input_str):
    str_short = input_str[6]
    return short_to_province(str_short)


def short_to_province(short):
    if short == "京":
        return "北京市"
    elif short == "津":
        return "天津市"
    elif short == "渝":
        return "重庆市"
    elif short == "沪":
        return "上海市"
    elif short == "冀":
        return "河北省"
    elif short == "晋":
        return "山西省"
    elif short == "辽":
        return "辽宁省"
    elif short == "吉":
        return "吉林省"
    elif short == "黑":
        return "黑龙江省"
    elif short == "苏":
        return "江苏省"
    elif short == "浙":
        return "浙江省"
    elif short == "皖":
        return "安徽省"
    elif short == "闽":
        return "福建省"
    elif short == "赣":
        return "江西省"
    elif short == "鲁":
        return "山东省"
    elif short == "豫":
        return "河南省"
    elif short == "鄂":
        return "湖北省"
    elif short == "湘":
        return "湖南省"
    elif short == "粤":
        return "广东省"
    elif short == "琼":
        return "海南省"
    elif short == "川" or short == "蜀":
        return "四川省"
    elif short == "黔" or short == "贵":
        return "贵州省"
    elif short == "云" or short == "滇":
        return "云南省"
    elif short == "陕" or short == "秦":
        return "陕西省"
    elif short == "甘" or short == "陇":
        return "甘肃省"
    elif short == "青":
        return "青海省"
    elif short == "台":
        return "台湾省"
    elif short == "蒙":
        return "内蒙古自治区"
    elif short == "桂":
        return "广西壮族自治区"
    elif short == "宁":
        return "宁夏回族自治区"
    elif short == "新":
        return "新疆维吾尔自治区 "
    elif short == "藏":
        return "西藏自治区"
    elif short == "港":
        return "香港特别行政区"
    elif short == "澳":
        return "澳门特别行政区"
    else:
        return "Not found"
