# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 10/10/2018 11:30
@File : main.py
@Des: 
'''

import pandas as pd
import os
import json
import re
import sys
from collections import Counter

province_pattern = "[1-9][0-9](0000)"
city_pattern = "[1-9]{2}([1-9][0-9]|[0-9][1-9]|[1-9][1-9])(00)"

def readData():
    df_entitydata = pd.read_csv("./../data/entitydata.csv")
    return df_entitydata


def contextSearch(code, county_name, type, oldyear, newyear, counter):
    res = []
    counter[type] += 1
    code = str(code) if not isinstance(code, str) else code
    filepath = "./../../data/{}.txt".format(newyear) if type == "add" else "./../../data/{}.txt".format(oldyear)

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


    # 处理二级地域：xx地区-->xx市
    if re.match(string=code, pattern=city_pattern) and not (code.startswith("11") or code.startswith("12") or code.startswith("31") or code.startswith("50")):
        try:
            index_ = mapping_file_key.index(code)
        except ValueError:
            counter["ValueError"] += 1
            return
        while index_ >= 0:
            tmp_code = mapping_file_key[index_]
            if re.match(pattern=province_pattern, string=tmp_code):
                province_code = tmp_code
                province_name = mapping_file[tmp_code].decode("utf-8")
                city_name = county_name
                counter[province_name] += 1
                res.extend([province_code])
                break
            index_ -= 1

        assert res
        assert index_ > 0
        filepath = "./../../data/{}.txt".format(newyear)
        # mapping_file
        mapping_file_new = {}
        mapping_file_key = []
        with open(filepath, "r") as input_file:
            for line in input_file.readlines():
                tmp = line.strip().split("\t")
                code_ = tmp[0]
                name = tmp[1]
                mapping_file_new[code_] = name
                mapping_file_key.append(code_)
        cands = []
        pre_code = res[0]
        if not (pre_code.startswith("71") or pre_code.startswith("81") or pre_code.startswith("82") or re.match(
                pattern=province_pattern, string=pre_code)):
            print "wrong code:", pre_code
        else:
            try:
                index_ = mapping_file_key.index(pre_code)
                while index_ < len(mapping_file_key):
                    index_ += 1
                    tmp_code = mapping_file_key[index_]
                    if re.match(pattern=city_pattern, string=tmp_code):
                        cands.append(tmp_code)
                    elif re.match(pattern=province_pattern, string=tmp_code):
                        break
            except:
                print "wrong code: ", pre_code, mapping_file[pre_code]
        candidates = [mapping_file_new[x] for x in cands]
        return candidates

    # 通用的处理
    else:
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
                # res.extend([province_name])
                res.extend([code])
                break
            # 直辖市下的市／区      11:北京; 12:天津; 31:上海; 50:重庆
            elif code.startswith("11") or code.startswith("12") or code.startswith("31") or code.startswith("50"):
                if re.match(pattern=province_pattern, string=tmp_code):
                    province_code = tmp_code
                    province_name = mapping_file[tmp_code].decode("utf-8")
                    city_name = county_name
                    counter[province_name] += 1
                    # res.extend([province_name,city_name])
                    res.extend([province_code])
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
                    # res.extend([province_name, city_name])
                    res.extend([province_code, city_code])
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



        assert res
        filepath = "./../../data/{}.txt".format(newyear)
        # mapping_file
        mapping_file_new = {}
        mapping_file_key = []
        with open(filepath, "r") as input_file:
            for line in input_file.readlines():
                tmp = line.strip().split("\t")
                code_ = tmp[0]
                name = tmp[1]
                mapping_file_new[code_] = name
                mapping_file_key.append(code_)
        cands = []
        if len(res) <= 1:
            pre_code = res[0]
            if not(pre_code.startswith("71") or pre_code.startswith("81") or pre_code.startswith("82") or re.match(pattern=province_pattern, string=pre_code)):
                print "wrong code:", pre_code
            else:
                try:
                    index_ = mapping_file_key.index(pre_code)
                    while index_ < len(mapping_file_key):
                        index_ += 1
                        tmp_code = mapping_file_key[index_]
                        if re.match(pattern=province_pattern, string=tmp_code) or re.match(pattern=city_pattern, string=tmp_code):
                            break
                        else:
                            cands.append(tmp_code)
                except:
                    print "wrong code: ", pre_code, mapping_file[pre_code]
        else:
            pre_code = res[1]
            try:
                index_ = mapping_file_key.index(pre_code)
                while index_ < len(mapping_file_key):
                    index_ += 1
                    tmp_code = mapping_file_key[index_]
                    if re.match(pattern=province_pattern, string=tmp_code) or re.match(pattern=city_pattern, string=tmp_code):
                        break
                    else:
                        cands.append(tmp_code)
            except:
                print "wrong code: ", pre_code, mapping_file[pre_code]
        candidates = [mapping_file_new[x] for x in cands]
        return candidates
    # return res


def process():
    df_entitydata = readData()

    for index, df_data in df_entitydata.iterrows():
        type = df_data["type"]
        target_e = df_data["name"]
        code = int(df_data["code"])
        level = int(df_data["level"])
        year = df_data["year"]
        year_old, year_new = [int(x) for x in year.split("-")]
        cand_e = df_data["entitys"].strip().replace("[", "").replace("]", "").split(",")
        cand_e = [x.strip() for x in cand_e]
        rel = df_data["rel"]

        # if not os.path.exists("./../../output/js_output_{}.txt_1line".format(year_old)):
        #     os.system("cd ./../../script; python dataTransform.py ./../data/{}.txt ./../output/js_output_{}.txt".format(year_old, year_old))
        # js_data_all = json.load("./../../output/js_output_{}.txt_1line".format(year_old))

        if type == "add":
            continue

        if rel == "-":
            continue

        counter = Counter()
        candidates = contextSearch(code, target_e, type, year_old, year_new, counter)
        candidates, cand_e = set(candidates), set(cand_e)
        new_e = list(candidates & cand_e)
        print "cand_e: ", json.dumps(list(cand_e), ensure_ascii=False, encoding="utf-8")
        print "candidates: ", json.dumps(list(candidates), ensure_ascii=False, encoding="utf-8")
        print target_e, rel, json.dumps(new_e, ensure_ascii=False, encoding="utf-8")
        print "-------------------------"



if __name__ == "__main__":
    process()