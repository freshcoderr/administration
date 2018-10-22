# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 10/10/2018 11:19
@File : genLabelData.py
@Des: 
'''

import re
import pandas as pd


def readdata():
    df_data = pd.read_csv("./labelData.csv")
    # print df_data
    extract = df_data["extract"].tolist()
    label = df_data["label"].tolist()
    extract_ = [x.decode("utf-8") for x in extract]
    label_ = [x.decode("utf-8") for x in label]
    return df_data, extract_, label_


def process():
    df_data, extract_, label_ = readdata()
    entitys = []
    for e, l in zip(extract_, label_):
        assert len(e) == len(l)
        start, end = [], []
        print "------------------------"
        for item in re.finditer(string=l, pattern=u"X+"):
            print item.start(), item.end()
            start.append(item.start())
            end.append(item.end())
        entity = []
        for st, en in zip(start, end):
            print e[st:en]
            entity.append(e[st:en])
        entitys.append(list(set(entity)))
    df_data["entitys"] = entitys
    df_data.to_csv("./entitydata.csv", encoding="utf-8", index=False)
    print "entity data saved in entitydata.csv."
    return True

if __name__ == "__main__":
    process()