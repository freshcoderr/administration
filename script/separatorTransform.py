# -*- coding: utf-8 -*-
'''
@Author : YuanXihao
@Time : 2018/8/10 下午4:31
@File : separatorTransform.py
@Des: del space in city_name, such as the data in 2016
'''
import pandas as pd
import sys
import os

def process(input_data, output_data, separator="\t"):
    if separator == ",":
        df_data = pd.read_csv(input_data, header=None)
    df_data = pd.read_table(input_data, header=None)
    df_outdata = pd.DataFrame()
    df_outdata[0] = df_data[0]
    tmp = []
    for i in df_data[1]:
        tmp.append(i.strip())
    df_outdata[1] = tmp
    df_outdata.to_csv(output_data, index=False)
    os.system('sed -i "s/,/\t/g" {}'.format(output_data))

if __name__ == "__main__":
    input_data = sys.argv[1]
    output_data = sys.argv[2]
    # separator = sys.argv[3]
    process(input_data, output_data)