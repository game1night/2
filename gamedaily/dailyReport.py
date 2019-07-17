#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2019/7/15 20:57

@author: tatatingting
"""

import time
from selenium import webdriver
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import jieba
import jieba.analyse
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
import datetime

# 解决画图中文乱码的问题
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题,或者转换负号为字符串


class dailyGet:

    def __init__(self, dr='', today=''):
        self.c = pd.DataFrame()
        if len(today) > 0:
            self.today = today
        else:
            # yesterday = datetime.date.today() + datetime.timedelta(-1)
            # self.today = str(yesterday)
            # print(self.today)
            self.today = time.strftime('%Y-%m-%d')
        self.filename = self.today
        self.num = 0
        self.dr = dr
        self.df = pd.DataFrame()

        # 配置司机
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        self.dr = webdriver.Chrome("./game1night/2/chromedriver", chrome_options=options)

    def run(self):
        n = 2
        # 打开网页
        print('正在打开网页，请稍等...')
        self.dr.get("https://www.gamersky.com/news")
        time.sleep(n)

        # 提取信息
        print('开始提取信息，请稍等...')
        titles = self.dr.find_elements_by_class_name('tit')
        m = min(500, max(200, len(titles)))
        if m == 500:
            print('what??? what??? what???')
        for i in range(1, m):
            print(i, '/', m)
            i = i % 50
            # fresh
            if i == 0:
                self.dr.find_element_by_link_text('下一页').click()
                time.sleep(n)
                print(i, '/', m)
            try:
                # find it
                xpath = '/html/body/div[7]/div[2]/div[1]/div[3]/ul/li[' + str(i) + ']'
                # date
                xpath_date = xpath + '/div[3]/div[2]/div[1]'
                # save it or not
                date = self.dr.find_element_by_xpath(xpath_date).text.strip()  # 2019-07-15 21:23
                date = date[:10]
                print(date, self.today)
                if date != self.today:
                    # break
                    continue
                else:
                    self.num += 1
                    # print(self.num)

                    # category
                    xpath_category = xpath + '/div[1]/a[1]'
                    # href, title
                    xpath_title = xpath + '/div[1]/a[2]'
                    # txt
                    xpath_brief = xpath + '/div[3]/div[1]'

                    # save them
                    category = self.dr.find_element_by_xpath(xpath_category).text.strip()
                    title = self.dr.find_element_by_xpath(xpath_title).text.strip()
                    href = self.dr.find_element_by_xpath(xpath_title).get_attribute('href').strip()
                    brief = self.dr.find_element_by_xpath(xpath_brief).text.strip()
                    c = pd.DataFrame({'num': [self.num],
                                      'date': [date],
                                      'category': [category],
                                      'title': [title],
                                      'href': [href],
                                      'brief': [brief]})
                    print('处理中间数据中...')
                    # 拼接
                    self.c = pd.concat((self.c, c))
                    # 去重
                    self.c.drop_duplicates(['brief'], inplace=True)
            except:
                pass

        # 关闭司机
        self.dr.close()
        self.dr.quit()
        print('网页已关闭，正在处理数据...')

        # 存储数据
        # filename
        print(self.c.shape)
        self.filename = self.today + '.csv'
        # with open('./data/' + self.filename, 'w', encoding='utf-8-sig') as f:
        #     for i in self.c:
        #         f.write(i)
        path = './game1night/2/gamedaily'
        self.c.to_csv(path+'/data/' + self.filename, encoding='utf-8-sig', index=False)

        print('数据已处理完毕')
        return self.df, self.today


class dataPre():

        def __init__(self, df, today):
            self.df = df
            self.today = today
            self.filename = self.today + '.csv'

        def run(self):
            path = './game1night/2/gamedaily'

            # 处理数据
            # 整理数据
            self.df = pd.read_csv(path+'/data/' + self.filename)
            print(self.df.shape)
            self.df.sort_values(by=['date', 'category', 'title', 'brief'], inplace=True)

            # ===概述
            analysis = self.df.category.value_counts()
            # 文
            txt0_c = ''
            for i in analysis.index:
                txt0_c += '{}（{}），'.format(str(i), str(analysis[i]))
            # 图
            analysis = analysis.sort_index().rename('counts_by_category')
            fig_title = self.today+'共收录'+str(self.df.shape[0])+'篇，涵盖' + str(analysis.shape[0]) + '个主题 @游戏夜读'
            analysis.plot(kind='bar', legend=True,
                          color='orange',
                          title=fig_title)
            plt.savefig(path+'/data/assets/img/' + self.today +'-topic.png')
            txt0 = '本期共收录{}篇，涉及{}个主题：{}信息来源：游民星空。\n\n'.format(str(self.df.shape[0]), str(analysis.shape[0]), txt0_c)

            # ===关键词
            txt1_raw = ''
            for i in self.df.brief:
                txt1_raw += str(i)
            # 去掉不重要的
            for i in ['…', '.', '．', '「', '」', '...', '!', '?', '？', '！']:
                txt1_raw = txt1_raw.replace(i, '')
            # 分词
            seg_list = jieba.cut(txt1_raw)
            sentence = ", ".join(seg_list)
            # 词云
            txt1_ciyun = ''
            for i in self.df.title:
                txt1_ciyun += str(i)
            seg_ciyun = jieba.cut(txt1_ciyun)
            sentence_ciyun = ", ".join(seg_ciyun)
            wordcloud = WordCloud(background_color='white',
                                  font_path=r'C:\Windows\Fonts\Deng.ttf',
                                  # mask=im_mask,
                                  stopwords=STOPWORDS).generate(sentence_ciyun)

            plt.imshow(wordcloud)
            plt.axis('off')
            # plt.show()
            wordcloud.to_file(path+'/data/assets/img/'+self.today+'-ciyun.png')
            # 提取关键词
            tags = jieba.analyse.extract_tags(sentence, topK=50, withWeight=False, allowPOS=())
            print(tags)
            # 准备输出
            txt1_c = '，'.join(tags)
            txt1 = '{}。\n\n'.format(txt1_c)

            # ===文摘内容
            txt = self.df.apply(lambda x: '#### [{} | {}]({}) \n\n{}\n\n\n'.format(
                x.category,
                x.title,
                x.href,
                x.brief), axis=1)

            # ===文档结构和内容
            self.filename = self.today + '-game1night-' + self.today + '.md'
            title = '游戏日报-{}'.format(self.today)
            with open(path+'/data/_posts/'+self.filename, 'w', encoding='utf-8-sig') as f:
                f.write('---\ntitle: "{}"\ncategories: game daily\nauthor: tingbot\n\n---\n\n\n'.format(title))

                f.write('Hi, morning! Here\'s Ting\'s Game Daily. What did I do yesterday? What will I do today? Are there any impediments in your way?\n\n')

                f.write('### Overview 概述\n\n')
                f.write('![{}]({})\n\n'.format(title+'-topic', '../assets/img/'+self.today+'-topic.png'))
                f.write(txt0)

                f.write('### Key words 关键词\n\n')
                f.write('![{}]({})'.format(title+'-ciyun', '../assets/img/'+self.today+'-ciyun.png'))
                
                f.write(txt1)

                f.write('### Summary 摘要\n\n')

            with open(path+'/data/_posts/'+self.filename, 'a', encoding='utf-8-sig') as f:
                for i in txt:
                    f.write(i)
                
                f.write('\n\nHere is "Ting\'s Game Daily" - a reference to the game. Produced by game1night, Tingbot is responsible for editing and publishing, looking forward to better performance. 早上好，这里是「叮！游戏日报」——收录有关游戏的参考资料。由game1night出品，Tingbot负责编辑和发布，期待更好的表现。\n\n')
                f.write('![{}]({})\n\n'.format(title+'-source', '../assets/img/0_game1night.png'))

            print(self.filename)
            return title


if __name__ == '__main__':
    df, today = dailyGet().run()
    dataPre(df, today).run()
