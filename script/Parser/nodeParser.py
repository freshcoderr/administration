# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/8/8 上午10:25
@File : nodeParser.py
@Des: parser
'''

import pandas as pd


class NodeParser(object):

    def __init__(self, js_data):
        self.js_data = js_data
        self.province = []
        self.city = []
        self.county = []
        self.nodeParser(js_data)

    def nodeParser(self, data):
        if isinstance(data, list):
            for item in data:
                self.nodeParser(item)
        if isinstance(data, dict):
            type = data.get("@type","-")
            if type == "province":
                id = data.get("@id","-")
                name = data.get("name","-")
                province_node = {":ID":id, "name":name, ":LABEL":"province", "level":1}
                self.province.append(province_node)
            elif type == "city":
                id = data.get("@id", "-")
                name = data.get("name", "-")
                city_node = {":ID": id, "name": name, ":LABEL": "city", "level":2}
                self.city.append(city_node)
            elif type == "county":
                id = data.get("@id", "-")
                name = data.get("name", "-")
                county_node = {":ID": id, "name": name, ":LABEL": "county", "level":3}
                self.county.append(county_node)

            for key, value in data.items():
                self.nodeParser(value)

    def data2csv(self, output_path):
        nodes = self.province + self.city + self.county
        df_nodes = pd.DataFrame(nodes)
        df_nodes.to_csv(output_path, index=False)
