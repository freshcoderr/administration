# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/8/8 上午10:26
@File : linkParser.py
@Des: parser
'''

import pandas as pd

class LinkParser(object):

    def __init__(self, js_data):
        self.js_data = js_data
        self.link = []
        self.linkParser(js_data)

    def linkParser(self, data):
        if isinstance(data, list):
            for item in data:
                self.linkParser(item)
        if isinstance(data, dict):
            type = data.get("@type", "-")
            if type == "province":
                end_id = data.get("@id")
                citys = data.get("city")    # dict
                if isinstance(citys, dict):
                    for key, value in citys.items():
                        start_id = value.get("@id")
                        link = {"o:END_ID": end_id, "p:TYPE":"located_in", "s:START_ID":start_id}
                        self.link.append(link)
            elif type == "city":
                end_id = data.get("@id")
                countys = data.get("county")    # list
                if isinstance(countys, list):
                    for county in countys:
                        start_id = county.get("@id")
                        link = {"o:END_ID": end_id, "p:TYPE": "located_in", "s:START_ID": start_id}
                        self.link.append(link)
            for key, value in data.items():
                self.linkParser(value)

    def data2csv(self, output_path):
        df_nodes = pd.DataFrame(self.link)
        df_nodes.to_csv(output_path, index=False)