#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2019/7/17 18:53

@author: tatatingting
"""

import os
import time
import datetime
from selenium import webdriver
import pandas as pd


def get_data():
    path0 = os.path.dirname(os.path.realpath(__file__))
    print(path0)
    path_1 = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    print(path_1)

    # 设置等待
    n = 2

    # 打开网页
    dr = webdriver.Chrome(os.path.join(path_1, 'chromedriver'))
    dr.get("https://www.gamersky.com/news")
    time.sleep(n)

    # 准备提取
    titles = dr.find_elements_by_class_name('tit')
    m = len(titles)
    yestoday = str(datetime.date.today() + datetime.timedelta(-1))
    num = 0
    df = pd.DataFrame()
    for i in range(1, m):
        i = i % 50
        if i == 0:
            dr.find_element_by_link_text('下一页').click()
        try:
            xpath = '/html/body/div[7]/div[2]/div[1]/div[3]/ul/li[' + str(i) + ']'
            xpath_date = xpath + '/div[3]/div[2]/div[1]'
            date = dr.find_element_by_xpath(xpath_date).text.strip()  # 2019-07-15 21:23
            date = date[:10]
            print(date, yestoday, i, num, m)
            if date != yestoday:
                continue
            else:
                num += 1
                xpath_category = xpath + '/div[1]/a[1]'
                category = dr.find_element_by_xpath(xpath_category).text.strip()
                xpath_title = xpath + '/div[1]/a[2]'
                title = dr.find_element_by_xpath(xpath_title).text.strip()
                href = dr.find_element_by_xpath(xpath_title).get_attribute('href').strip()
                xpath_brief = xpath + '/div[3]/div[1]'
                brief = dr.find_element_by_xpath(xpath_brief).text.strip()
                c = pd.DataFrame({'num': [num],
                                  'date': [date],
                                  'category': [category],
                                  'title': [title],
                                  'href': [href],
                                  'brief': [brief],
                                  'source': 'youminxingkong'
                                  })
                df = pd.concat((df, c))
                df.drop_duplicates(['brief'], inplace=True)
        except:
            pass

    # 关闭司机
    dr.close()
    dr.quit()

    # 处理数据
    today = time.strftime('%Y-%m-%d')
    filename = today + '-youminxingkong.csv'
    df.to_csv(os.path.join(path0, 'data', filename), encoding='utf-8-sig', index=False)
    print(df.shape)


if __name__ == '__main__':
    st = time.time()
    get_data()
    et = time.time()
    print('wow~ {}'.format(et - st))
