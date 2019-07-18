#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2019/7/17 22:15

@author: tatatingting
"""

import os
import time
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import jieba
import jieba.analyse
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

# 解决画图中文乱码的问题
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题,或者转换负号为字符串

path0 = os.path.dirname(os.path.realpath(__file__))
print(path0)
path_1 = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(path_1)
today = time.strftime('%Y-%m-%d')
path1 = os.path.join(path0, 'data')
print(path1)


def clean(df):
    df.drop_duplicates(keep='last', inplace=True)


def read_lib(filename):
    path = os.path.join(path1, filename)
    df = pd.read_csv(path, encoding='utf-8-sig')
    return df


def add_lib(filename, d):
    path = os.path.join(path1, filename)
    df = pd.read_csv(path, encoding='utf-8-sig')
    clean(df)
    df = df.append(d, ignore_index=True)
    df.to_csv(path, encoding='utf-8-sig', index=False)
    return df


def read_source(today, source=''):
    filename = today + '-' + source + '.csv'
    df = pd.read_csv(os.path.join(path0, 'data', filename), encoding='utf-8-sig')
    return df


def pre_publish():
    # source
    source = read_lib('source.csv')
    clean(source)
    # articles
    df = pd.DataFrame()
    for i in source.source:
        df_new = read_source(today, i)
        df = pd.concat((df, df_new))
    clean(df)
    df.sort_values(by=['category', 'title', 'brief'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    # history
    history = add_lib('history.csv', {'date': today, 'num': df.shape[0]})
    clean(history)
    history.date = history.date.apply(lambda x: pd.to_datetime(x))
    history.sort_values(by='date', ascending=True, inplace=True)
    history['cumsum'] = history.num.cumsum()
    history.sort_values(by='date', ascending=False, inplace=True)
    history['date_str'] = history.date.apply(lambda x: x.strftime('%Y-%m-%d'))

    # data
    num_article = df.shape[0]
    num_topic = df.category.unique().shape[0]

    df1 = df.category.value_counts()
    c1 = []
    for i in df1.index:
        if i == df1.shape[0] - 1:
            c1.append('{}({})。'.format(i, df1[i]))
        else:
            c1.append('{}({})，'.format(i, df1[i]))

    c2 = ''
    for i in df.brief:
        c2 += str(i)
    c2 = ", ".join(jieba.cut(c2))
    tags = jieba.analyse.extract_tags(c2, topK=50, withWeight=False, allowPOS=())

    c3 = ''
    for i in df.title:
        c3 += str(i)
    c3 = ', '.join(jieba.cut(c3))
    fig_keywords_filename = today + '-ciyun.png'
    wordcloud = WordCloud(background_color='white',
                          font_path=r'C:\Windows\Fonts\Deng.ttf',
                          stopwords=STOPWORDS).generate(c3)

    plt.imshow(wordcloud)
    plt.axis('off')
    wordcloud.to_file(os.path.join(path0, 'assets', 'img', 'gamedaily', fig_keywords_filename))

    # content
    c = ''
    filename = today + '-game1night-' + today + '.md'
    filepath = os.path.join(path0, '_posts', filename)
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(c)

    def a(c):
        with open(filepath, 'a', encoding='utf-8-sig') as f:
            f.write(c)
        c = ''
        return c

    c += '---\n'
    c += 'title: "叮！游戏日报-{}"\n'.format(today)
    c += 'categories: game daily\n'
    c += 'author: tingbot\n'
    c += '---\n\n\n'
    c += 'Hi, morning! What did I do yesterday? What will I do today? Are there any impediments in my way?\n\n'
    c += '#### Overview 概述\n\n'
    c += '本期共收录{}篇，涉及{}个主题：'.format(num_article, num_topic, ''.join(c1))
    # ===
    c = a(c)
    for i in df1.index:
        if i == df1.shape[0] - 1:
            c1.append('{}({})。\n\n'.format(i, df1[i]))
        else:
            c1.append('{}({})，'.format(i, df1[i]))
    c += '#### Kew words 关键词\n\n'
    c += '![ting\'s-game-daily-today-keywords]({})\n\n'.format('../assets/img/gamedaily/' + fig_keywords_filename)
    c += '{}。\n\n'.format('，'.join(tags))
    c += '#### Summary 摘要\n\n'
    # ===
    c = a(c)
    for i in df.index:
        c += '##### [{}]({})\n\n'.format(df.loc[i, 'title'], df.loc[i, 'href'])
        c += '{}\n\n'.format(df.loc[i, 'brief'])
    c += '#### References 来源\n\n'
    # ===
    c = a(c)
    for i in source.index:
        c += '- {}：{} \n\n'.format(source.loc[i, 'name'], source.loc[i, 'url'])
    c += '#### Intro 简介\n\n'
    c += '![ting\'s-game-daily-intro]({})\n\n'.format('../assets/img/gamedaily/0_game1night.png')
    c += 'Here is "Ting\'s Game Daily" - a reference to the game. Produced by game1night, Tingbot is responsible for editing and publishing. Looking forward to better performance.\n\n'
    c += '早上好，这里是“叮！游戏日报”——收录有关游戏的参考资料。由game1night出品，由Tingbot编辑和发布。期待更好的表现。\n\n'
    c += '#### Yestodays 目录\n\n'
    # ===
    c = a(c)
    for i in history.index:
        c += '##### [Ting\'s Game Daily {}]({}) （当日收录{}条，累计收录{}条）\n\n'.format(history.loc[i, 'date_str'],
                                                                              'https://tatatingting.github.io/post/' +
                                                                              history.loc[
                                                                                  i, 'date_str'] + '-game1night-' +
                                                                              history.loc[i, 'date_str'],
                                                                              history.loc[i, 'num'],
                                                                              history.loc[i, 'cumsum'])
    c += '感谢阅读。'

    # ===
    c = a(c)


if __name__ == '__main__':
    pre_publish()
