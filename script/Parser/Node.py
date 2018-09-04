# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/8/14 上午10:32
@File : Node.py
@Des: 
'''

import logging
import json

class Node(object):

    def __init__(self, year, js_data):
        # self.name = ""
        # self.code = ""
        # self.type = ""
        # self.level = 0
        self.year = year
        # self.context1 = None
        # self.context2 = None
        self.js_data = js_data
        self.jsParser()

    def jsParser(self):
        node_ = json.load(self.js_data)
        self.name = node_.get("name", "-")
        self.code = node_.get("@id", "-")
        self.type = node_.get("@type", "-")
        self.level = node_.get("level", "-")
        self.context = node_.get("context", "-")

    @staticmethod
    def equalNode(node1, node2):
        propertys = ["name", "@id", "@type", "level"]
        for property in propertys:
            if getattr(node1, property) == getattr(node2, property):
                continue
            else:
                return False
        return True

    def getContext(self, node):
        context = node.get("context", [])
        return context
