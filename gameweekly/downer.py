#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2020/4/8 11:40

@author: tatatingting
"""

import os
from selenium import webdriver
import time
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import jieba
import jieba.analyse
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2


def cd(n, flag=False):
    for i in range(n):
        time.sleep(1)
        if flag:
            print(i)

    return None


def start_car(path):
    # 设置驱动
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # 创建汽车
    driver = webdriver.Chrome(os.path.join(path, 'chromedriver'), options=options)
    return driver


def get_data_youmin(driver, date_str, filename):
    # 前往首页
    url = 'https://www.gamersky.com/news/'
    driver.get(url)
    # 开始寻找合适的文章
    count = 1
    count_miss = 0
    while count > 0:
        if count % 50 == 0:
            driver.find_element_by_link_text('下一页').click()
            cd(3)
        else:
            i = count % 50
            # 标题和时间页卡
            article_title_item = driver.find_element_by_xpath(
                '/html/body/div[7]/div[2]/div[1]/div[3]/ul/li[{}]/div[1]/a[2]'.format(str(i)))
            article_date_item = driver.find_element_by_xpath(
                '/html/body/div[7]/div[2]/div[1]/div[3]/ul/li[{}]/div[3]/div[2]/div[1]'.format(str(i)))
            # 进入视野
            # driver.execute_script("arguments[0].scrollIntoView();", article_title_item)
            # 提取时间进行比对
            article_date = article_date_item.get_attribute('textContent').strip()
            article_date = pd.to_datetime(article_date[:10])
            if article_date in date_str:
                # 确认过眼神后提取信息
                article_title = article_title_item.get_attribute('textContent').strip()
                article_url = article_title_item.get_attribute('href').strip()
                article_source = 'youminxingkong'
                # 组织信息准备存储
                new_content = '{},{},{},{}'.format(
                    article_date,
                    article_title,
                    article_url,
                    article_source,
                )
                uu(filename, new_content, 'a')
                print('{}, {}, +1'.format(count, article_date))
                # 树立flag准备跳出循环的条件
                if count_miss == 0:
                    count_miss = 1
            else:
                if count_miss > 0:
                    count_miss += 1
                if count_miss > 10:
                    break

        # 下一篇
        count += 1

    return None


def uu(filename, content, mode='a'):
    with open(filename, mode, encoding='utf-8-sig') as f:
        f.write('\n' + content)
    # cd(1)
    return None


def get_data_tidy(filename, today, path):
    df = pd.read_csv(filename)
    print(df.shape)
    df.drop_duplicates(inplace=True)
    print(df.shape)
    # 获取词云图
    fig_ciyun_path = get_ciyun_pic(df.loc[:, 'title'], today, path)
    # 加水印
    color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
    watermark_new(fig_ciyun_path, color)

    return None


def get_ciyun_pic(df, today, path):
    c3 = ''
    for i in df:
        c3 += str(i)
    c3 = ', '.join(jieba.cut(c3))
    wordcloud = WordCloud(background_color='white',
                          font_path=r'C:\Windows\Fonts\Deng.ttf',
                          colormap='tab20',
                          width=1280,
                          height=376,
                          stopwords=STOPWORDS).generate(c3)
    plt.imshow(wordcloud)
    plt.axis('off')
    fig_ciyun_path = os.path.join(path, 'img', '{}-ciyun.png'.format(today))
    wordcloud.to_file(fig_ciyun_path)

    return fig_ciyun_path


def watermark_new(filepath, color, content='游戏夜读（game1night）', ratio=0):
    im = Image.open(filepath)

    # 处理im
    changdu = 10
    im = im.resize((im.size[0], im.size[1]-changdu))
    im = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    # im = cv2.resize(im, (300, 280), interpolation=cv2.INTER_CUBIC)
    im = cv2.copyMakeBorder(im, 0, changdu, 0, 0, cv2.BORDER_CONSTANT, value=[255 - j for j in color])
    # im = cv2.copyMakeBorder(im, 0, 20, 0, 0, cv2.BORDER_REFLECT)
    im = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    # 处理watermark
    watermark = Image.new('RGBA', im.size)
    draw = ImageDraw.Draw(watermark, 'RGBA')
    font = ImageFont.truetype("simsun.ttc", changdu, encoding="unic", index=1)
    # x y 坐标
    draw.text((20, im.size[1] - changdu), content, font=font, fill=(255, 255, 255))
    # 旋转ji度
    watermark = watermark.rotate(ratio, Image.BICUBIC)
    # 透明的
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.7)
    watermark.putalpha(alpha)
    # 合成新的图片
    image2 = Image.composite(watermark, im, watermark)
    image2.save(filepath.replace('.png', '..png'))
    print(color, [256 - j for j in color])

    return None


def run():
    # 获取当前地址的父母
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path2 = os.path.dirname(os.path.realpath(__file__))
    # 初始化文件名
    today = time.strftime('%Y-%m-%d')
    filename = '{}.csv'.format(today)
    filename = '{}_{}.csv'.format(today, time.time())
    # 搜集前的准备工作
    date = pd.date_range('2020-04-10', '2020-04-17')  #2
    print(date)
    # 开始搜集阅读
    dr = start_car(path)
    # 初始化标题行
    uu(filename, 'date,title,url,source', 'w')
    # 获取新闻内容
    get_data_youmin(dr, date, filename)
    # 最后整理
    get_data_tidy(filename, today, path2)

    return None


if __name__ == '__main__':
    run()
