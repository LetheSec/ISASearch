# -*- coding: utf-8 -*-
# @Time    : 2020/5/25 16:21
# @Author  : Yuan.XJ
# @File    : main.py


from scrapy.cmdline import execute

import sys
import os

# 防止log信息到stderr(https://www.jianshu.com/p/62f41ec59071)
sys.stderr = sys.stdout

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "xianzhi"])
# execute(["scrapy", "crawl", "anquanke"])
# execute(["scrapy", "crawl", "sihou"])