# -*- coding: utf-8 -*-

import scrapy
import re
import json
from items import RegioncrawlerItem
import ConfigParser

PATTERN1 = '((?:<a name="(?:历史沿革|建制沿革|建置沿革)" class="lemma-anchor " ></a>){1}(?:.|\n)*(?:<a name="行政区划" class="lemma-anchor " ></a>){1})'
PATTERN2 = '((?:>)(?:[^<>a-zA-Z\n])+(?:<))'
# originDataPath = "/Users/yuanxihao/work/coder/python_workplace/grad_project/administration/data/crawler/1999-2000/origin.txt"

class RegionspiderSpider(scrapy.Spider):
    name = 'regionSpider'
    allowed_domains = ['baike.baidu.com']
    start_urls = ['http://baike.baidu.com/']
    search_list = ["崇文区"]

    def __init__(self):
        super(RegionspiderSpider, self).__init__()
        conf = ConfigParser.SafeConfigParser()
        conf.read("./../scrapy.cfg")
        self.originDataPath = conf.get("inputpath", "originDataPath")

    def dictparse(self, data, res):
        if isinstance(data, list):
            for item in data:
                self.dictparse(item, res)
        if isinstance(data, dict):
            # if data.has_key(u"level") and data.get(u"type") == u"add":
            if data.has_key(u"level") :
                res.append(data)
            else:
                for key, value in data.items():
                    self.dictparse(value, res)


    def start_requests(self):
        jsonfile = open(self.originDataPath, "r")
        search_data = json.load(jsonfile)
        # jsonfile.close()

        search_list = []
        self.dictparse(search_data, search_list)
        for data in search_list:
            item = RegioncrawlerItem()
            print "data:", data
            item["name"] = data.get(u"name", "-").encode("utf-8")
            item["code"] = data.get(u"code", "-").encode("utf-8")
            item["level"] = data.get(u"level", "-")
            item["type"] = data.get(u"type", "-").encode("utf-8")
            search_url = self.start_urls[0] + "item" + "/" + item["name"]
            print "search url:", search_url
            yield scrapy.Request(url=search_url, meta={"item": item}, callback=self.parse)


    def parse(self, response):
        # print "response:", response.body
        # print type(response.body)
        item = response.meta["item"]
        res = re.findall(pattern=PATTERN1, string=response.body)
        if res:
            res1 = res[0]
            # print "res1:", res1
            res2 = re.findall(pattern=PATTERN2, string=res1)
            # print "res2:", json.dumps(res2, ensure_ascii=False, encoding='utf-8', indent=4)
            result = "".join(res2).replace(">","").replace("<","")
            print item["name"], ":", result
            item["text"] = result
            yield item
        else:
            print item["name"], ":", "-"
            item["text"] = "-"
            yield item
