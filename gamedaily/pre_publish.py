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
    df.reset_index(drop=True, inplace=True)


def read_lib(filename):
    path = os.path.join(path1, filename)
    df = pd.read_csv(path, encoding='utf-8-sig')
    clean(df)
    return df


def add_lib(filename, d):
    path = os.path.join(path1, filename)
    df = pd.read_csv(path, encoding='utf-8-sig')
    clean(df)
    df = df.append(d, ignore_index=True)
    clean(df)
    df.to_csv(path, encoding='utf-8-sig', index=False)
    return df


def read_source(today, source=''):
    filename = today + '-' + source + '.csv'
    df = pd.read_csv(os.path.join(path0, 'data', filename), encoding='utf-8-sig')
    clean(df)
    return df


def get_df(source):
    df = pd.DataFrame()
    for i in source.source:
        df_new = read_source(today, i)
        df = pd.concat((df, df_new))
    clean(df)
    df.sort_values(by=['category', 'title', 'brief'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def update_history(df):
    history = add_lib('history.csv', {'date': today, 'num': df.shape[0]})
    history.date = history.date.apply(lambda x: pd.to_datetime(x))
    history.sort_values(by='date', ascending=True, inplace=True)
    history['cumsum'] = history.num.cumsum()
    history.sort_values(by='date', ascending=False, inplace=True)
    history['date_str'] = history.date.apply(lambda x: x.strftime('%Y-%m-%d'))
    return history


d_topic = {
    '出台': ['消息', 1],
    '政策': ['消息', 1],
    '开发': ['人物', 2],
    '制作': ['人物', 2],
    '卖': ['交易', 3],
    '买': ['交易', 3],
    '价': ['交易', 3],
    '年': ['历史', 4],
    '月': ['历史', 4],
    '曾经': ['历史', 4],
    '%': ['数据', 5],
    '增长': ['数据', 5],
    '减少': ['数据', 5],
    '同比': ['数据', 5],
    '环比': ['数据', 5],
    '？': ['讨论', 6],
    '?': ['讨论', 6],
    '吗': ['讨论', 6],
    '如何': ['讨论', 6],
    '什么': ['讨论', 6],
    '怎么': ['讨论', 6],
    '登陆': ['发行', 7],
    '发布': ['发行', 7],
    '发售': ['发行', 7],
    '热搜': ['发行', 7],
    '上线': ['发行', 7],
    '新游': ['发行', 7],
    '《': ['作品', 8],
}


def cal_topic(title, category, source):
    for key in d_topic.keys():
        if key in title:
            return [key, d_topic.get(key)[0], d_topic.get(key)[1]]
    if len(category) == 0:
        return ['source', source, '999']
    else:
        return ['category', category, '999']


def get_topic(df):
    df['topic_list'] = df.apply(lambda row: cal_topic(row['title'], row['category'], row['source']), axis=1)
    df['topic'] = df.topic_list.apply(lambda x: x[1])
    df['topic_point'] = df.topic_list.apply(lambda x: x[2])
    df1 = df.topic.value_counts()
    c1 = []
    for i in df1.index:
        c1.append('{}({})'.format(i, df1[i]))
    num_topic = len(c1)
    return c1, num_topic


def get_tags(df):
    c2 = ''
    for i in df.brief:
        c2 += str(i)
    c2 = ", ".join(jieba.cut(c2))
    tags = jieba.analyse.extract_tags(c2, topK=50, withWeight=False, allowPOS=())
    return tags


def get_ciyun(df):
    c3 = ''
    for i in df.title:
        c3 += str(i)
    c3 = ', '.join(jieba.cut(c3))
    fig_ciyun_path = today + '-ciyun.png'
    wordcloud = WordCloud(background_color='white',
                          font_path=r'C:\Windows\Fonts\Deng.ttf',
                          stopwords=STOPWORDS).generate(c3)
    plt.imshow(wordcloud)
    plt.axis('off')
    wordcloud.to_file(os.path.join(path0, 'assets', 'img', 'gamedaily', fig_ciyun_path))
    fig_ciyun_path = '../assets/img/gamedaily/' + fig_ciyun_path
    return fig_ciyun_path


def get_init_md():
    c = ''
    filename = today + '-game1night-' + today + '.md'
    filepath = os.path.join(path0, '_posts', filename)
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(c)
    return c, filepath


def update_md(c, filepath):
    with open(filepath, 'a', encoding='utf-8-sig') as f:
        f.write(c)
    c = ''
    return c


def pre_publish():
    # ====== 统计数据 ======
    # 获取 信息来源登记册
    source = read_lib('source.csv')
    # 获取 文章收录登记册
    df = get_df(source)
    # 更新 历史收录登记册
    history = update_history(df)
    # 今日 文章收录数目
    num_article = df.shape[0]
    # 今日 文章涉及的主题
    c1, num_topic = get_topic(df)
    df.sort_values(by=['topic_point', 'topic', 'title', 'source'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    # 今日 关键词-摘要
    tags = get_tags(df)
    # 今日 关键词-词云图-标题
    fig_ciyun_path = get_ciyun(df)

    # ====== 博客模板 ======
    # 新建空文档
    c, filepath = get_init_md()

    # 组织内容结构
    # （1）开头yaml信息
    c += '---\n'
    c += 'title: "游戏日报-{}"\n'.format(today)
    c += 'categories: game daily\n'
    c += 'author: tingbot\n'
    c += '---\n\n\n'
    # （2）开场白
    c += 'Hi, morning! What did I do yesterday? What will I do today? Are there any impediments in my way?\n\n'
    # （3）概述
    c += '#### Overview 概述\n\n'
    c += '本期共收录{}篇，涉及{}个主题：'.format(num_article, num_topic)
    c += '{}。\n\n'.format('，'.join(c1))
    # （4）关键词
    c += '#### Kew words 关键词\n\n'
    c += '![game-daily-today-keywords]({})\n\n'.format(fig_ciyun_path)
    c += '{}。\n\n'.format('，'.join(tags))
    # （5）摘要
    c += '#### Summary 摘要\n\n'
    for i in df.index:
        c += '##### [{} | {}]({})\n\n'.format(df.loc[i, 'topic'], df.loc[i, 'title'], df.loc[i, 'href'])
        c += '{}\n\n'.format(df.loc[i, 'brief'])
    # （6）来源
    c += '#### References 来源\n\n'
    for i in source.index:
        c += '- {}：[{}]({}) \n\n'.format(source.loc[i, 'name'], source.loc[i, 'url'], source.loc[i, 'url'])
    # （7）简介
    c += '#### Intro 简介\n\n'
    c += 'Here is ting\'s Game Daily - a reference to the game. Produced by game1night, Tingbot is responsible for editing and publishing. Looking forward to better performance.\n\n'
    c += '早上好，这里是“叮！游戏日报”——收录有关游戏的参考资料。由game1night出品，由Tingbot编辑和发布。期待更好的表现。\n\n'
    c += '![game-daily-intro]({})\n\n'.format('../assets/img/gamedaily/0_game1night.png')
    # （8）目录
    c += '#### Yestodays 近期收录\n\n'
    for i in history.index[:7]:
        c += '##### [Game Daily {}]({}) （当日收录{}条，累计{}条）\n\n'.format(history.loc[i, 'date_str'],
                                                                    'https://tatatingting.github.io/post/' +
                                                                    history.loc[
                                                                        i, 'date_str'] + '-game1night-' +
                                                                    history.loc[i, 'date_str'],
                                                                    history.loc[i, 'num'],
                                                                    history.loc[i, 'cumsum'])
    # （9）尾声
    c += '感谢阅读。'

    # ====== 更新一波文档 ======
    print(len(c))
    c = update_md(c, filepath)


if __name__ == '__main__':
    pre_publish()
    print('今日文章输出完毕！')
