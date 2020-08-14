#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2020/7/19 1:12

@author: tatatingting
"""

'''
行业历史资金流
- 获取算法
    连续2个取不到href/a则放弃
    得到61个行业代号，依次进行新网页打开，提取数据
- 数据结构
    行业名称，日期，资金流 / 一个行业存一次，mode='a'
    list.append, dict.update
- 分析结果
    level 1： 每个行业统一在一张图中
- 参考资料：
http://quote.eastmoney.com/center/boardlist.html#industry_board 有领涨股票
http://data.eastmoney.com/bkzj/BK0738.html
href="//quote.eastmoney.com/unify/r/90.BK0738"

http://stock.eastmoney.com/hangye.html
http://data.eastmoney.com/bkzj/474.html
//*[@id="main"]/div[1]/div[2]/div[3]/ul/li[{}]
//*[@id="main"]/div[1]/div[2]/div[3]/ul/li[2]/a
//*[@id="main"]/div[1]/div[2]/div[3]/ul/li[{}]/a
//*[@id="main"]/div[1]/div[2]/div[3]/ul/li[79]/a
/html/body/div[1]/div/div[2]/div[1]/div[2]/div[3]/ul/li[2]/a
//*[@id="main"]/div[1]/div[2]/div[3]/ul/li[75]/a
//*[@id="tb_lishi"]/tbody/tr[1]/td[1]
//*[@id="tb_lishi"]/tbody/tr[4]/td[1]
//*[@id="tb_lishi"]/tbody/tr[102]/td[1]
//*[@id="tb_lishi"]/tbody/tr[{}]/td[1]
//*[@id="tb_lishi"]/tbody/tr[1]/td[2]/span
//*[@id="tb_lishi"]/tbody/tr[102]/td[2]/span
'''

import os
from selenium import webdriver
import time
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['STZhongsong']    # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False           # 解决保存图像是负号'-'显示为方块的问题


def start_car(path):
    # 设置驱动
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    # 创建汽车
    driver = webdriver.Chrome(os.path.join(path, 'chromedriver'), options=options)
    print('go')
    return driver


def get_hangye(dr, history_dict, url, number_xpath):
    # 前往指定网页
    dr.get(url)
    # 获取行业代号和名称，共61个
    n_count = 0
    n = 0
    while n_count < 61:
        n += 1
        try:
            item_class = dr.find_element_by_xpath(number_xpath[:-2].replace('000', str(n))).get_attribute('class')
            if item_class == 'list_li':
                hangye_code_item = dr.find_element_by_xpath(number_xpath.replace('000', str(n)))
                hangye_title = hangye_code_item.get_attribute('title').strip()
                hangye_number = hangye_code_item.get_attribute('href').strip()[-8:-5]
                history_dict.update({hangye_title: hangye_number})
                n_count += 1
        except:
            print('pass')
    print('dict done')


def get_history(dr, history_dict, url_2, date_xpath, net_xpath, filename, m_count):
    n = 0
    for hangye_title, hangye_number in history_dict.items():
        # 前往相应网页
        dr.get(url_2.replace('000', hangye_number))
        # 提取历史数据
        m = 1
        history_list = []
        while m <= m_count:
            # history_date_item = dr.find_element_by_xpath(date_xpath.replace('000', str(m)))
            # history_date = history_date_item.get_attribute('textContent').strip()
            # history_date = pd.to_datetime(history_date)
            # history_net_item = dr.find_element_by_xpath(net_xpath.replace('000', str(m)))
            # history_net = history_net_item.get_attribute('textContent').strip()
            history_date = pd.to_datetime(dr.find_element_by_xpath(date_xpath.replace('000', str(m))).get_attribute('textContent').strip())
            history_net = dr.find_element_by_xpath(net_xpath.replace('000', str(m))).get_attribute('textContent').strip()
            if '万' in history_net:
                # history_net = history_net.replace('万', '')
                # history_net = int(float(history_net) * 10000)
                history_net = int(float(history_net.replace('万', '')) * 10000)
            elif '亿' in history_net:
                # history_net = history_net.replace('亿', '')
                # history_net = int(float(history_net) * 100000000)
                history_net = int(float(history_net.replace('亿', '')) * 100000000)
            history_list.append([hangye_title, history_date, history_net])
            m += 1
        pd.DataFrame(history_list).to_csv(filename, mode='a', encoding='utf-8-sig', index=False, header=False)
        n += 1
        print(hangye_title, n)


def run(filename, m_count):
    # 获取当前相对地址的上级，驱动所在
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # 开始启动汽车
    dr = start_car(path)
    # 前往指定地点，开始作业
    url = 'http://stock.eastmoney.com/hangye.html'
    number_xpath = '//*[@id="main"]/div[1]/div[2]/div[3]/ul/li[000]/a'
    url_2 = 'http://data.eastmoney.com/bkzj/000.html'
    date_xpath = '//*[@id="tb_lishi"]/tbody/tr[000]/td[1]'
    net_xpath = '//*[@id="tb_lishi"]/tbody/tr[000]/td[2]/span'
    history_dict = {}
    get_hangye(dr, history_dict, url, number_xpath)
    # print(history_dict)
    get_history(dr, history_dict, url_2, date_xpath, net_xpath, filename, m_count)
    # print(history_dict)


def tidy_data(filename):
    print('plot')
    df = pd.read_csv(filename, encoding='utf-8-sig', parse_dates=[1], header=None)
    df.columns = ['hangye', 'date', 'capture']
    df = df.drop_duplicates(keep='last')
    df = df.sort_values(by=['date', 'hangye'])
    df.to_csv(filename, mode='w', encoding='utf-8-sig', index=False, header=False)
    print(df.shape)

    df = df.pivot_table(index=['date'], columns=['hangye'])
    print(df.shape)
    df.columns = [col[1] for col in df.columns]

    # 确定回溯天数（自然日）
    number = 100

    # 0-60 原始数据；61- 累加值
    df = df.iloc[-number:, :].copy()
    for col in df.columns:
        df[col+'-累加'] = df[col].cumsum()
    ddd = df.copy()

    # (0)
    # print('\n单日绝对值比较\n')
    df3 = df.iloc[-number:, :61].copy()
    # for back_day in [-3, -2, -1]:
    #     df3 = df3.sort_values(by=df3.index[back_day], axis=1, ascending=False)
    #     cols = df3.columns
    #     print('昨日最多：{}, 最少：{}'.format(cols[:3], cols[-3:]))
    # print(df3.iloc[:, :3].tail())
    # df3.iloc[:, :].plot

    # (1)
    # print('\n单日绝对值比较\n')
    df4 = df.iloc[-number:, :61].copy()
    # 除以最大绝对值的归一化，暂不用
    max_abs_number = df4.abs().max().max()
    print('最大的绝对值是：', max_abs_number)
    df4 = df4 / int(max_abs_number)
    # 按照整体排序
    cols = df4.abs().max().sort_values(ascending=False).index
    # 画图
    # df4.loc[:, cols[:12]].plot()
    # 单日幅度靠前的
    # print('\n单日幅度靠前的\n', df4.loc[:, cols[:12]].columns)
    list1 = pd.DataFrame(index=cols, data=range(1, len(cols) + 1)).sort_index()
    list1 = list1.reset_index(drop=False)
    list1.columns = ['hangye', 'rank_daily']
    # print(list1)
    # 按照最近排序
    # df4 = df4.sort_values(by=df4.index[-1], axis=1, ascending=True)
    # df4.iloc[:, -20:].plot()
    # 分批画图
    # df4.loc[:, cols[:32]].plot()
    # df4.loc[:, cols[-32:]].plot()

    # (2)
    # print('\n累加值的排名\n')
    # 排名算法（暂时弃用）
    # df1 = df.iloc[-number:, :61]
    # df1.rank().plot()
    df2 = df.iloc[-number:, 61:].copy()
    # 同起点算法（第一行数据的差异）（向量思维
    df2 = df2 - df2.iloc[0, :]
    # 按照某一天进行排序
    for back_day in [-3, -2, -1]:
        df2 = df2.sort_values(by=df2.index[back_day], axis=1, ascending=False)
        cols = df2.columns
        # print('昨日最多：{}, 最少：{}'.format(cols[:3], cols[-3:]))
    # print(df2.iloc[:, :3].tail())
    # print(df2.iloc[:, -3:].tail())
    # 累计垫底的
    # df2.iloc[:, -12:].plot()
    # print('\n累计垫底的\n', df2.loc[:, cols[-12:]].columns)
    # 累计靠前的
    # df2.iloc[:, :12].plot()
    # print('\n累计靠前的\n', df2.loc[:, cols[:12]].columns)
    # 累计排名
    cols = [(str(i).replace('-累加', '')) for i in df2.columns]
    list2 = pd.DataFrame(index=cols, data=range(1, len(cols) + 1)).sort_index()
    list2 = list2.reset_index(drop=False)
    list2.columns = ['hangye', 'rank_cunsum']
    # print(list2)
    # 分批画图
    # df2.iloc[:, :32].plot()
    # df2.iloc[:, -32:].plot()

    list3 = pd.merge(list1, list2, how='outer')
    list3['rank_all'] = list3['rank_daily'] + list3['rank_cunsum']
    list3['rank_all2'] = list3['rank_daily'] + 62 - list3['rank_cunsum']
    list3['rank_all3'] = list3['rank_daily'] - 62 + list3['rank_cunsum']
    list3 = list3.sort_values('rank_daily', ascending=True).set_index('hangye')
    # list3['index'] = range(1, 122, 2)
    print(list3)
    list3.ix[:, ['rank_all3']].plot(kind='bar', grid=True)
    if ddd.sum().sum() == df.sum().sum():
        plt.show()


if __name__ == '__main__':
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'history_capture.csv')
    m_count = 10
    run(filename, m_count)
    tidy_data(filename)
