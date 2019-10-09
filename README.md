2 - python scripts of news-spider, data clean and text analysis

## Ting's Game Daily

### Intro

It's a bunch of game news actually.

Nowadays the news are about games. It would be changed in the near future since I have receive a new request for finance information. All are game related. Isn't it?

There will be the list of the sources of the news meaning where are they pulled from. And almost every efforts would be spent for being more convenience and efficient.

It becomes reality because so much news and so little time, also so lazy as I am. Well, the result has been posted on [ting's blogs](https://tatatingting.github.io/) and you can goto check out. Since this project is built under the [LICENSE](./LICENSE) of GPL 3.0 so you can share it under it. If any issue, let me know. Thanks.

### Start

运行脚本即可。以下举例说明。

某日获取目标地址的新闻概要，进行本地整理后生成日报，再通过GitHub主页完成云端展示。要求：在本项目文件夹同级目录下，另有个人主页项目文件夹。Windows系统中，可以通过PowerShell运行如下代码：

```
$today=Get-Date
$today=$today.ToString('yyyy-MM-dd')

python .\game1night\2\gamedaily\youminxingkong.py
python .\game1night\2\gamedaily\pre_publish.py

#del .\game1night\2\gamedaily\data\$today-youminxingkong.csv

move .\game1night\2\gamedaily\_posts\$today-game1night-$today.md  .\tatatingting.github.io\_posts
move .\game1night\2\gamedaily\assets\img\gamedaily\$today-ciyun.png  .\tatatingting.github.io\assets\img\gamedaily

cd .\tatatingting.github.io
git add .
git status
git commit -a -m'add gamedaily-game1night'
git push
git status

pause

```



### Rebuild

1. 范围，目标：新闻标题，摘要，关键词，描述统计；半自动化抓取、管理、展示。
2. 抓取。
3. 整理。
4. 展示。
5. 代码优化：文件路径。

