# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/8/20 上午10:08
@File : entityLinking.py
@Des: file1(new); file2(old);
    discover no linking entity
'''

import os
import logging
import sys
import json
from collections import Counter
import re

province_pattern = "[1-9][0-9](0000)"
city_pattern = "[1-9]{2}([1-9][0-9]|[0-9][1-9]|[1-9][1-9])(00)"

def loadData(filepath):
    mapping = {}
    with open(filepath, "r") as input_file:
        for line in input_file.readlines():
            tmp = line.strip().split("\t")
            code = tmp[0]
            name = tmp[1]
            mapping[code] = name
    return mapping

def saveData(res):
    path = os.path.abspath('.')
    filepath = path+"/crawler/{}".format(res["year"])
    if not os.path.exists(filepath):
        os.system("cd {}; mkdir {}".format(path+"/crawler", res["year"]))
    out_f = open(filepath + "/origin.txt", "w")
    print >> out_f, json.dumps(res, ensure_ascii=False, encoding='utf-8', indent=4)

def search(code_list, change_file, mapping_file, mapping_file_key, type, counter, res):

    for code in code_list:
        counter[type] += 1
        county_name = change_file[code]
        try:
            index_ = mapping_file_key.index(code)
        except ValueError:
            counter["ValueError"] += 1
            continue
        city_code = 0
        while index_ >= 0:
            tmp_code = mapping_file_key[index_]
            # 直辖市下的市／区      11:北京; 12:天津; 31:上海; 50:重庆
            if code.startswith("11") or code.startswith("12") or code.startswith("31") or code.startswith("50"):
                if re.match(pattern=province_pattern, string=tmp_code):
                    province_code = tmp_code
                    province_name = mapping_file[tmp_code]
                    city_name = county_name
                    counter[province_name] += 1
                    if res.get(province_name):
                        res[province_name].append({"type":type, "name":city_name, "code":code, "level":2})
                    else:
                        res[province_name] = [{"type":type, "name":city_name, "code":code, "level":2}]
                    # print province_name, city_name, county_name
                    break

            else:
                if not city_code:
                     if re.match(pattern=city_pattern, string=tmp_code):
                        city_code = tmp_code
                        city_name = mapping_file[tmp_code]
                if re.match(pattern=province_pattern, string=tmp_code):
                    province_code = tmp_code
                    province_name = mapping_file[tmp_code]
                    counter[province_name] += 1
                    if res.get(province_name):
                        if res[province_name].get(city_name):
                            res[province_name][city_name].append({"type":type, "name":county_name, "code":code, "level":3})
                        else:
                            res[province_name][city_name] = [{"type":type, "name":county_name, "code":code, "level":3}]
                    else:
                        res[province_name] = {city_name:[{"type":type, "name":county_name, "code":code, "level":3}]}
                    # print province_name,city_name,county_name
                    break
            index_ -= 1
    return res

def process(in_file1, in_file2):
    res = {}
    year_old = re.findall(pattern='\d+', string=in_file2)[0]
    year_new = re.findall(pattern='\d+', string=in_file1)[0]
    res["year"] = year_old + "-" + year_new

    file1_key = []
    file2_key = []
    with open(in_file1, "r") as in_f1:
        for line in in_f1.readlines():
            file1_key.append(line.strip().split("\t")[0])
    with open(in_file2, "r") as in_f2:
        for line in in_f2.readlines():
            file2_key.append(line.strip().split("\t")[0])

    counter = Counter()
    file1 = loadData(in_file1)
    file2 = loadData(in_file2)

    os.system("sh ./../script/cal_entitylinking.sh {} {}".format(in_file1, in_file2))
    namechange_file = "{}_{}_has_name_changed".format(in_file1, in_file2)
    add_file = "{}_has_{}_no".format(in_file1, in_file2)
    del_file = "{}_has_{}_no".format(in_file2, in_file1)

    # os.system("pwd")
    namechange = loadData("./tmp/" + namechange_file)
    add = loadData("./tmp/" + add_file)
    delete = loadData("./tmp/" + del_file)

    res = search(add.keys(), add, file1, file1_key, "add", counter, res)
    res = search(delete.keys(), delete, file2, file2_key, "del", counter, res)
    res = search(namechange.keys(), namechange, file1, file1_key, "just_name_change", counter, res)
    print json.dumps(res, ensure_ascii=False, encoding="utf-8", indent=4), len(res)
    print json.dumps(counter, ensure_ascii=False, encoding="utf-8", indent=4)

    saveData(res)

if __name__ ==  "__main__":
    in_file1 = sys.argv[1]
    in_file2 = sys.argv[2]
    process(in_file1, in_file2)


'''
usage:
cd os.path.abspath('.');
python entityLinking.py new.txt old.txt
'''