# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/9/11 下午2:44
@File : run.py
@Des: 
'''

import sys
import os
import logging

def run_origin2table(s_year, e_year):
    logging.info("running origin2table...")
    for i in range(s_year, e_year+1):
        logging.info("year:{}-{}".format(i, i+1))
        os.system("python origin2table.py ../data/crawler/{}-{}/crawler.txt".format(i, i+1))
    logging.info("year {}-{} origin2table complete.".format(s_year, e_year))

def run_entitylinking(s_year, e_year):
    logging.info("running entitylinking...")
    for i in range(s_year, e_year+1):
        logging.info("year:{}-{}".format(i, i + 1))
        os.system("cd ../data; python entityLinking.py {}.txt {}.txt".format(i + 1, i))
    logging.info("year {}-{} entitylinking complete.".format(s_year, e_year))

def process():

    run_entitylinking(2007, 2016)

    run_origin2table(2007, 2016)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    process()