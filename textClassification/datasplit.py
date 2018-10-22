# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/9/13 下午2:48
@File : datasplit.py
@Des: input: alldata.csv
    output: validdata.csv
'''

import os
import pandas as pd
import sys
import jieba

STOPWORDS = "./stopwords.txt"


def dataGet():
    df_data = pd.DataFrame()
    for i in range(2007, 2016 + 1):
        data = pd.read_csv("./../data/crawler/{}-{}/data2label.csv".format(i, i + 1))
        data["year"] = "{}-{}".format(i, i + 1)
        df_data = df_data.append(data, ignore_index=True)
    df_data.to_csv("./data/allData.csv", index=False)
    print df_data


def stopwordsGet(filepath):
    stopwords = []
    global stopwords
    assert os.path.exists(filepath)
    with open(filepath, "r") as file:
        for word in file.readlines():
            # print type(word)
            stopwords.append(word.decode("utf-8").strip('\n'))
    return stopwords


def jiebaCut(raw):
    seg_list = jieba.cut(raw["extract"])
    new_seg_list = []
    if stopwords:
        # type(seg): unicode; type(stopwords): list(unicode)
        for seg in seg_list:
            if seg not in stopwords:
                new_seg_list.append(seg)
    return " ".join(new_seg_list)

def reltypeTrans(raw):
    rel = raw["rel"]
    if rel == "新增区" or rel == "新增县" or rel == "新增市":
        return "新增县／市／区"
    else:
        return rel

def initJieba():
    if not os.path.exists("./userdict.txt"):
        userdict = []
        for i in range(2007, 2016 + 1):
            filepath = "./../data/{}.txt".format(i)
            with open(filepath, "r") as file:
                for line in file.readlines():
                    name = line.strip().split("\t")[1]
                    userdict.append(name)
        userdict = set(userdict)
        o_file = open("./userdict.txt", "w")
        for word in userdict:
            print >> o_file, word + " " + "100"
        o_file.close()
    jieba.load_userdict("./userdict.txt")
    jieba.enable_parallel(4)


def process():

    if not os.path.exists("./data/allData.csv"):
        dataGet()

    if STOPWORDS:
        stopwordsGet(STOPWORDS)

    initJieba()

    df_data = pd.read_csv("./data/allData.csv")
    all_valid_data = df_data[df_data["extract"]!="-"].dropna()
    all_valid_data.to_csv("./data/allData.csv", index=False)
    print all_valid_data

    valid_data = pd.DataFrame()
    valid_data["name"] = all_valid_data["name"]
    valid_data["context"] = all_valid_data["context"]
    valid_data["code"] = all_valid_data["code"]
    valid_data["level"] = all_valid_data["level"]
    valid_data["type"] = all_valid_data["type"]
    valid_data["extract"] = all_valid_data.apply(jiebaCut, axis=1, raw=True)
    # valid_data["rel"] = all_valid_data["rel"]
    valid_data["rel"] = all_valid_data.apply(reltypeTrans, axis=1, raw=True)
    valid_data["year"] = all_valid_data["year"]
    valid_data.to_csv("./data/validData.csv", index=False, encoding="utf-8")
    print valid_data



if __name__ == "__main__":

    process()
    # stopwordsGet(STOPWORDS)


'''
usage:
python datasplit.py
'''