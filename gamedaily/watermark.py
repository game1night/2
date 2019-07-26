#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2019/7/21 8:55

@author: tatatingting
"""

import time
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import numpy as np
import random

"""图片水印生成器，自定义文字，颜色，大小，位置"""


# 颜色倾斜位置水印
def auto_make_watermark1(
        filepath,
        savefilepath,
        radio=0,
        x=50,
        y=50,
        content="Posted on ting's blogs.",
        color=(random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
):
    """
    :param filepath: 图片路径
    :param content: 水印文字
    :param color: 水印颜色
    :param savefilepath: 保存路径
    :param radio: 水印倾斜角度
    :return:
    """
    im = Image.open(filepath)
    watermark = Image.new('RGBA', im.size)
    draw = ImageDraw.Draw(watermark, 'RGBA')
    font = ImageFont.truetype("simsun.ttc", 15, encoding="unic", index=1)
    # x y 坐标
    draw.text((x, y), content, font=font, fill=color)
    # 旋转ji度
    watermark = watermark.rotate(radio, Image.BICUBIC)
    # 透明的
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.7)
    watermark.putalpha(alpha)
    # 合成新的图片
    image2 = Image.composite(watermark, im, watermark)
    image2.save(savefilepath)


# 扩充颜色倾斜位置水印
def auto_make_watermark2(filepath,
                         savefilepath,
                         radio=0,
                         x=50,
                         y=50,
                         content="Posted on ting's blogs.",
                         color=(random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
                         ):
    """
    :param filepath: 图片路径
    :param content: 水印文字
    :param color: 水印颜色
    :param savefilepath: 保存路径
    :param radio: 水印倾斜角度
    :return:
    """
    im = Image.open(filepath)

    # 处理im
    im = im.resize((im.size[0], im.size[1]-20))
    im = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    # im = cv2.resize(im, (300, 280), interpolation=cv2.INTER_CUBIC)
    im = cv2.copyMakeBorder(im, 0, 20, 0, 0, cv2.BORDER_CONSTANT, value=[255-j for j in color])
    # im = cv2.copyMakeBorder(im, 0, 20, 0, 0, cv2.BORDER_REFLECT)
    im = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    # 处理watermark
    watermark = Image.new('RGBA', im.size)
    draw = ImageDraw.Draw(watermark, 'RGBA')
    font = ImageFont.truetype("simsun.ttc", 18, encoding="unic", index=1)
    # x y 坐标
    draw.text((20, 180), content, font=font, fill=color)
    # 旋转ji度
    watermark = watermark.rotate(radio, Image.BICUBIC)
    # 透明的
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.7)
    watermark.putalpha(alpha)
    # 合成新的图片
    image2 = Image.composite(watermark, im, watermark)
    image2.save(savefilepath)
    print(color, [256-j for j in color])


if __name__ == '__main__':
    time1 = time.time()
    for i in ['2019-07-26-ciyun',
              ]:
        filepath = './assets/img/gamedaily/{}.png'.format(i)
        savefilepath = './assets/img/gamedaily/{}_'.format(i)
        text = "Posted on ting's blogs."

        auto_make_watermark1(filepath, savefilepath+'1.png')
        auto_make_watermark2(filepath, savefilepath+'2.png')

    time2 = time.time()
    print('总共耗时：' + str(time2 - time1) + 's')
