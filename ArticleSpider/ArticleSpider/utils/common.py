# -*- coding: utf-8 -*-
# @Time    : 2020/5/26 1:03
# @Author  : Yuan.XJ
# @File    : common.py

import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


# if __name__ == '__main__':
#     print(get_md5('http://www.baidu.com'))
