# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RegioncrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    # 年份，例如：【2015->2016】
    year = scrapy.Field()

    # 上位：province
    # province = scrapy.Field()

    # 上位：city
    # city = scrapy.Field()

    # 当前地域名称
    name = scrapy.Field()

    # 当前地域行政代码
    code = scrapy.Field()

    # 当前地域处于第几级行政区
    level = scrapy.Field()

    # 属于那种更改
    type = scrapy.Field()

    # 当前地域的百科语料【历史沿革】
    text = scrapy.Field()
