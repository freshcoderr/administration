# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/9/17 下午12:18
@File : Train.py
@Des: train data
'''

import pandas as pd
import numpy as np
import xgboost as xgb
import json
import sys
import re
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

InputDataPath = "./../data/validData.csv"
Labelmapping = {"-": 0,
                "撤县（市）设区": 1,
                "撤县设市": 2,
                "合并": 3,
                "新增县／市／区": 4,
                "撤地区设市": 5,
                "更名": 6,
                "归属变化": 7,
                "撤销": 8,
                "分解": 9}


class Train(object):

    def __init__(self, feature):
        self.feature_ = feature


    def read_data(self):
        df_validData = pd.read_csv(InputDataPath)
        corpus = [x.decode("utf-8") for x in df_validData["extract"].tolist()]
        label = df_validData["rel"].tolist()
        return corpus, label

    def label2num(self, label_dict):
        return [Labelmapping[l] for l in label_dict]

    def feature(self, feature = 1):
        corpus_, label_ = self.read_data()
        # 根据 "行政区域是否发生改变" 来分类，一共是2类; 0: 未改变， 1: 改变
        if feature == 2:
            corpus = corpus_
            label_num = self.label2num(label_)
            label = [0 if x in [0, 1, 2, 5, 6, 7] else 1 for x in label_num]
        # 把 "撤县设市" 和 "撤县（市）设区" 归为一类
        elif feature == 3:
            corpus = corpus_
            Labelmapping["撤县设市"] = 1
            Labelmapping["分解"] = 2
            label = self.label2num(label_)
        else:
            corpus = corpus_
            label = self.label2num(label_)
        numclass = len(set(label))
        return corpus, label, numclass

    def train(self, method = "xgboost"):
        # x_train, x_test, y_train, y_test = self.read_data()
        corpus, label, numclass = self.feature(feature=self.feature_)

        print "label: ", Counter(label)
        print "numclass: ", numclass
        print "------------------------------------------------"

        x_train, x_test, y_train, y_test = train_test_split(corpus, label, test_size=0.2)
        print "train num: ", len(y_train)
        print "test num: ", len(y_test)
        print "------------------------------------------------"

        vectorizer = CountVectorizer()
        tfidftransformer = TfidfTransformer()
        tfidf = tfidftransformer.fit_transform(vectorizer.fit_transform(x_train))
        weight = tfidf.toarray()
        print "weight.shape: ", weight.shape
        test_tfidf = tfidftransformer.transform(vectorizer.transform(x_test))
        test_weight = test_tfidf.toarray()
        print "test_weight.shape: ", test_weight.shape
        print "------------------------------------------------\n"

        # city count feature
        x_train_count = np.array([self.city_count_feature(x) for x in x_train])
        x_test_count = np.array([self.city_count_feature(x) for x in x_test])
        assert len(weight) == len(x_train_count)
        assert len(test_weight) == len(x_test_count)
        weight = np.concatenate((weight, x_train_count), axis=1)
        test_weight = np.concatenate((test_weight, x_test_count), axis=1)
        # for i in range(len(weight)):
        #     weight[i] = np.append(weight[i], x_train_count[i])
        #     test_weight[i] = np.append(test_weight[i], x_test_count[i])
        print "weight.shape: ", weight.shape
        print "test_weight.shape: ", test_weight.shape
        # sys.exit(0)

        print "---------------------- train --------------------------"
        xgbtrain = xgb.DMatrix(weight, label=y_train)
        xgbtest = xgb.DMatrix(test_weight, label=y_test)
        param = {'max_depth': 6, 'eta': 0.05, 'eval_metric': 'merror', 'silent': 1, 'objective': 'multi:softmax',
                 'num_class': numclass}  # 参数
        evallist = [(xgbtrain, 'train'), (xgbtest, 'test')]
        num_round = 100  # 循环次数
        bst = xgb.train(param, xgbtrain, num_round, evallist)
        # save model
        bst.save_model("./../model/TC{}.model".format(self.feature_))
        preds = bst.predict(xgbtest)
        print "------------------------------------------------"

        count = 0
        for i in range(80):
            if preds[i] == y_test[i]:
                count += 1
        print "precision: ", count * 1.0 / len(y_test)

        good_cases = []
        bad_cases = []
        valid_data = pd.read_csv(InputDataPath)
        label_mapping_convert = self.caseAnalysis()
        print "------------------ case analysis ------------------"
        for i in range(len(y_test)):
            # good case
            if y_test[i] == preds[i]:
                goodcase = {"case":"good"}
                index = 0
                while index < 399:
                    if valid_data["extract"][index].decode("utf-8") == x_test[i]:
                        break
                    index += 1
                goodcase["index"] = index
                for key, value in valid_data.iloc[index].items():
                    goodcase[key] = value
                goodcase["label"] = y_test[i]
                goodcase["predict"] = int(preds[i])
                goodcase["predict_text"] = label_mapping_convert[preds[i]]
                good_cases.append(goodcase)
            # bad case
            else:
                badcase = {"case": "bad"}
                index = 0
                while index < 399:
                    if valid_data["extract"][index].decode("utf-8") == x_test[i]:
                        break
                    index += 1
                badcase["index"] = index
                for key, value in valid_data.iloc[index].items():
                    badcase[key] = value
                badcase["label"] = y_test[i]
                badcase["predict"] = int(preds[i])
                badcase["predict_text"] = label_mapping_convert[preds[i]]
                bad_cases.append(badcase)
        print "------------------ good case  ------------------"
        print json.dumps(good_cases, ensure_ascii=False, encoding="utf-8", indent=4)
        print "------------------ bad case  ------------------"
        print json.dumps(bad_cases, ensure_ascii=False, encoding="utf-8", indent=4)

        print "------------------------------------------------"
        print "precision: ", count * 1.0 / len(y_test)

    def caseAnalysis(self):
        label_mapping_convert = {}
        if self.feature_ == 1:
            for k, v in Labelmapping.items():
                label_mapping_convert[v] = k
        elif self.feature_ == 2:
            label_mapping_convert = {0: "行政区域未改变",
                                     1: "行政区域改变"}
        elif self.feature_ == 3:
            label_mapping_convert = {0: "-",
                                    1: "撤县（市）设区 / 撤县设市",
                                    2: "分解",
                                    3: "合并",
                                    4: "新增县／市／区",
                                    5: "撤地区设市",
                                    6: "更名",
                                    7: "归属变化",
                                    8: "撤销"}
        else:
            pass
        return label_mapping_convert


    # string example: "2010 年 月 国务院 批复 同意 撤销 北京市 西城区 宣武区 设立 新 北京市 西城区 以原 西城区 宣武区 行政区域"
    # return [3, 4]
    def city_count_feature(self, string):
        PATTERN = u".+[县|市|区|州|旗]$"
        feature, count = [0.0, 0.0], 0.0
        word_list = string.strip().split(" ")
        for word in word_list:
            if word == u"撤销":
                count = 0.0
            if word == (u"设立" or u"并入"):
                feature[0] = count
                count = 0.0
            if re.match(PATTERN, word):
                count += 1.0
        feature[1] = count
        # print "feature:", feature
        return feature



'''
# feature=2: 根据 "行政区域是否发生改变" 来分类，一共是2类; 0: 未改变， 1: 改变
# feature=3: 把 "撤县设市" 和 "撤县（市）设区" 归为一类
'''
def process():
    train = Train(3)
    train.train()

def test():
    train = Train(3)
    train.train()

if __name__ == "__main__":
    process()
    # test()