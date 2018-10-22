# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 07/10/2018 03:08
@File : train.py
@Des: 
'''

import pandas as pd
import re
from sklearn.model_selection import train_test_split
import os
import sys

USERDICTPATH = "./../data/userdict.txt"
VALIDDATA = "./../data/validData.csv"

class Train(object):

    def __init__(self):
        self.userdict = []
        self.altername = []
        self.read_txt()
        pass

    def read_txt(self):
        with open(USERDICTPATH, "r") as userdict_file:
            for line in userdict_file.readlines():
                name, weight = line.strip().split(" ")
                self.userdict.append(name.decode("utf-8"))
        self.userdict.remove(u"城区")

    def alterName(self):
        pattern1 = u"(.+)(?:特别行政区|自治[县区州旗])$"
        pattern2 = u"([^自治]+)(?:[县市区旗])$"
        for name in self.userdict:
            if re.match(pattern=pattern1, string=name):
                altername = re.findall(string=name, pattern=pattern1)[0]
                print name, altername
                self.altername.append(altername)
            elif re.match(pattern=pattern2, string=name):
                altername = re.findall(string=name, pattern=pattern2)[0]
                print name, altername
                if len(altername)>=2:
                    self.altername.append(altername)
        return self.altername


    def labelData(self):
        df_data = pd.read_csv(VALIDDATA)
        extract = df_data["extract"].tolist()
        label_list = []
        for line in extract:
            new_line = line.decode("utf-8")
            for name in self.userdict:
                # new_line = new_line.replace(name, "X" * (len(name) / 3))
                new_line = new_line.replace(name, "X" * len(name))
            for name in self.altername:
                new_line = new_line.replace(name, "X" * len(name))
            label = ""
            for w in new_line:
                if w == " ":
                    label += " "
                elif w == "X":
                    label += "X"
                else:
                    label += "O"
            # print label
            print line
            print label
            label_list.append(label)
        # print len(label_list)
        df_data["label"] = label_list
        # print label_list
        # print df_data

        df_data.to_csv("./../data/labelData.csv", encoding="utf8", index=False)

    def datasplit(self):
        df_data = pd.read_csv("./../data/labelData.csv")
        df_train = df_data.iloc[:300, :]
        df_test = df_data.iloc[300:350, :]
        df_valid = df_data.iloc[350:, :]
        self.tmp(df_train, "./../data/train.txt")
        # self.tmp(df_test, "./../data/test.txt")
        self.tmp(df_valid, "./../data/valid.txt")
        testfile = open("./../data/test2.txt", "w")
        for item in df_test["extract"].tolist():
            print >> testfile, item.replace(" ", ",")

    def tmp(self, df_data, filepath):
        data = df_data["extract"].tolist()
        label = df_data["label"].tolist()
        outfile = open(filepath, "w")
        for index, item in enumerate(data):
            print >> outfile, (u"^ " + " ".join(item.decode("utf-8").replace(" ","")) + u" $").encode("utf-8")
            print >> outfile, (u"O " + " ".join(label[index].decode("utf-8").replace(" ", "")) + u" O").encode("utf-8")
            print u"^ " + " ".join(item.decode("utf-8").replace(" ", "")) + u" $"
            print u"O " + " ".join(label[index].decode("utf-8").replace(" ", "")) + u" O"
        outfile.close()

train = Train()
train.labelData()
train.datasplit()