# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/9/5 上午10:18
@File : origin2table.py
@Des: restore origin data to table so as to easily tag the data
'''

import pandas as pd
import json
import sys
import re
import logging
from collections import Counter

OUTPUTPATH = ""
province_pattern = "[1-9][0-9](0000)"
city_pattern = "[1-9]{2}([1-9][0-9]|[0-9][1-9]|[1-9][1-9])(00)"

def loadData(in_path):
    with open(in_path, "r") as in_f:
        for line in in_f.readlines():
            yield json.loads(line)

def saveData():
    pass

# mode: strict; loose
def corpusExtract(string_, old_year, new_year, mode="strict"):
    # year = new_year if type == "add" else old_year
    string = string_.encode("utf-8")
    corpus = string.strip().split("。")
    index, sentence = 0, []
    for index, sentence_ in enumerate(corpus):
        if old_year in sentence_ or new_year in sentence_:
            sentence.append(sentence_)
    if mode == "loose" and not sentence:
        year = [int(old_year)-2,
                int(old_year)-1,
                int(old_year),
                int(new_year),
                int(new_year)+1,
                int(new_year)+2]
        for index, sentence_ in enumerate(corpus):
            for year_ in year:
                if str(year_) in sentence_:
                    sentence.append(sentence_)
    return " | ".join(sentence).decode("utf-8") if sentence else u"-"


def contextSearch(code, county_name, type, oldyear, newyear, counter):
    res = []
    counter[type] += 1

    filepath = "./../data/{}.txt".format(newyear) if type == "add" else "./../data/{}.txt".format(oldyear)

    # mapping_file
    mapping_file = {}
    mapping_file_key = []
    with open(filepath, "r") as input_file:
        for line in input_file.readlines():
            tmp = line.strip().split("\t")
            code_ = tmp[0]
            name = tmp[1]
            mapping_file[code_] = name
            mapping_file_key.append(code_)


    # county_name = change_file[code]
    try:
        index_ = mapping_file_key.index(code)
    except ValueError:
        counter["ValueError"] += 1
        return
    city_code = 0
    while index_ >= 0:
        tmp_code = mapping_file_key[index_]
        # 特别行政区     71：台湾； 81：香港； 82：澳门
        if code.startswith("71") or code.startswith("81") or code.startswith("82"):
            province_name = mapping_file[tmp_code].decode("utf-8")
            city_name = county_name
            counter[province_name] += 1
            res.extend([province_name])
            break
        # 直辖市下的市／区      11:北京; 12:天津; 31:上海; 50:重庆
        elif code.startswith("11") or code.startswith("12") or code.startswith("31") or code.startswith("50"):
            if re.match(pattern=province_pattern, string=tmp_code):
                province_code = tmp_code
                province_name = mapping_file[tmp_code].decode("utf-8")
                city_name = county_name
                counter[province_name] += 1
                res.extend([province_name,city_name])
                # if res.get(province_name):
                #     res[province_name].append({"type":type, "name":city_name, "code":code, "level":2})
                # else:
                #     res[province_name] = [{"type":type, "name":city_name, "code":code, "level":2}]
                # print province_name, city_name, county_name
                break

        else:
            if not city_code:
                 if re.match(pattern=city_pattern, string=tmp_code):
                    city_code = tmp_code
                    city_name = mapping_file[tmp_code].decode("utf-8")
            if re.match(pattern=province_pattern, string=tmp_code):
                province_code = tmp_code
                province_name = mapping_file[tmp_code].decode("utf-8")
                counter[province_name] += 1
                res.extend([province_name, city_name])
                # if res.get(province_name):
                #     if res[province_name].get(city_name):
                #         res[province_name][city_name].append({"type":type, "name":county_name, "code":code, "level":3})
                #     else:
                #         res[province_name][city_name] = [{"type":type, "name":county_name, "code":code, "level":3}]
                # else:
                #     res[province_name] = {city_name:[{"type":type, "name":county_name, "code":code, "level":3}]}
                # print province_name,city_name,county_name
                break
        index_ -= 1
    return res

def process(input_path):
    counter = Counter()
    res = []
    old_year, new_year = input_path.split("/")[3].split("-")
    year_mapping = {"del": old_year, "add": new_year}
    for data in loadData(input_path):
        output = {}
        output["text"] = data["text"]
        try:
            output["extract"] = corpusExtract(data["text"], old_year, new_year, "loose")
        except KeyError:
            counter["Keyerror_text"] += 1
        # --------------------------------------------------
        # output["extract"] = u"test"
        # --------------------------------------------------
        output["code"] = data["code"]
        output["type"] = data["type"]
        output["level"] = data["level"]
        output["name"] = data["name"]
        output["context"] = contextSearch(output["code"], output["name"], output["type"], old_year, new_year, counter)
        output["rel"] = ""
        res.append(output)
    # print output
    # print json.dumps(res, ensure_ascii=False, encoding="utf-8", indent=4)
    df_output = pd.DataFrame(res,columns=["name", "context", "code", "level", "type", "text", "extract", "rel"],)

    # print df_output

    # save data
    df_output.to_csv("../data/crawler/{}-{}/data2label.csv".format(old_year, new_year), encoding="utf-8", index=False)

if __name__ == "__main__":
    input_path = sys.argv[1]
    process(input_path)

'''
usage:
    python origin2table.py ../data/crawler/2015-2016/crawler.txt
'''