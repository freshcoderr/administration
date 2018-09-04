# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import ConfigParser

# outputDataPath = "/Users/yuanxihao/work/coder/python_workplace/grad_project/administration/data/crawler/1999-2000/crawler4read.txt"
# outputDataPath2 = "/Users/yuanxihao/work/coder/python_workplace/grad_project/administration/data/crawler/1999-2000/crawler.txt"

class RegioncrawlerPipeline(object):

    def __init__(self):
        conf = ConfigParser.SafeConfigParser()
        conf.read("./../scrapy.cfg")
        outputDataPath = conf.get("outputpath", "outputDataPath")
        outputDataPath2 = conf.get("outputpath", "outputDataPath2")
        self.f = open(outputDataPath, "w")
        self.f2 = open(outputDataPath2, "w")

    def process_item(self, item, spider):
        print "item", type(item)
        output = {}
        for k, v in item.items():
            output[k] = v
        print >> self.f, json.dumps(output, ensure_ascii=False, encoding='utf-8', indent=4)+"\n"
        print >> self.f2, json.dumps(output, ensure_ascii=False, encoding='utf-8')
        return item

    def close(self):
        self.f.close()
        self.f2.close()