# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/8/7 下午5:13
@File : dataTransform.py
@Des: transform origin data to json
'''


import re
import sys
import json
import logging
import collections
from Parser.nodeParser import NodeParser
from Parser.linkParser import LinkParser

province_pattern = "[1-9][0-9](0000)"
city_pattern = "[1-9]{2}([1-9][0-9]|[0-9][1-9]|[1-9][1-9])(00)"


def stat(code_list):
    province_count = 0
    city_count = 0
    county_count = 0
    for code in code_list:
        if re.match(pattern=province_pattern, string=code):
            province_count += 1
        elif re.match(pattern=city_pattern, string=code):
            city_count += 1
        else:
            county_count += 1
    logging.info("province: {}, city: {}, county: {}".format(province_count, city_count, county_count))


def stat2(js_out, counter):
    if isinstance(js_out, list):
        for item in js_out:
            stat2(item, counter)
    if isinstance(js_out, dict):
        type = js_out.get("@type","-")
        counter[type] += 1
        for key, value in js_out.items():
            if isinstance(value, list) or isinstance(value, dict):
                stat2(value, counter)


def save_data(out_file_path, result):
    out_file = open(out_file_path, "w")
    print >> out_file, json.dumps(result, ensure_ascii=False, encoding="utf-8", indent=4)
    out_file.close()
    logging.info("data saved to '{}'".format(out_file_path))


def load_data(in_file_path):
    file2dict = {}
    with open(in_file_path, "r") as in_file:
        for line in in_file.readlines():
            line_list = line.strip().split("\t")
            id = line_list[0]
            city = line_list[1]
            file2dict[id] = city
    return file2dict


def transform(code_list, file2_dict):
    rs = {}
    rs_city = {}
    current_province = ""
    current_city = ""
    for code in code_list:
        if re.match(pattern=province_pattern, string=code):
            province = file2_dict[code]
            if current_province != province:
                if rs_city:
                    rs[current_province]["city"] = rs_city
                current_province = province
                rs[current_province] = {"code": code, "name":current_province,"@type": "province", "@id": code}
                rs_city = {}
        elif re.match(pattern=city_pattern, string=code):
            city = file2_dict[code]
            if current_city != city:
                current_city = city
                rs_city[current_city] = {"code": code,"name":current_city, "@type": "city", "@id": code, "county": []}
        else:
            county = file2_dict[code]
            # 直辖市下的市／区      11:北京; 12:天津; 31:上海; 50:重庆
            if code.startswith("11") or code.startswith("12") or code.startswith("31") or code.startswith("50"):
                rs_city[county] = {"code": code, "name": county,"@type": "city", "@id": code, "county": []}
            else:
                rs_county = {"code": code, "@type": "county", "@id": code, "name": county}
                rs_city[current_city]["county"].append(rs_county)

    return rs


def process(in_file_path, out_file_path):
    # step 1, load data
    logging.info("load data from '{}'".format(in_file_path))
    file2dict = load_data(in_file_path)
    code_list = file2dict.keys()
    code_list.sort()
    stat(code_list)

    # step 2, data transform
    logging.info("transform data ...")
    js_out = transform(code_list, file2dict)

    # step 3, save data
    counter = collections.Counter()
    stat2(js_out, counter)
    save_data(out_file_path, js_out)
    for key, value in counter.items():
        logging.info("{}: {}".format(key, value))

    # generate nodes.csv
    nodes = NodeParser(js_out)
    nodes.data2csv("../output/nodes.csv")

    # generate links.csv
    links = LinkParser(js_out)
    links.data2csv("../output/links.csv")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    in_file_path = sys.argv[1]
    out_file_path = sys.argv[2]
    process(in_file_path, out_file_path)

'''
usage:
python dataTransform.py ./../data/xx.txt ./../output/js_output_xx.txt
'''