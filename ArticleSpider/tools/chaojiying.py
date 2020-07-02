# -*- coding: utf-8 -*-
# @Time    : 2020/6/8 14:40
# @Author  : Yuan.XJ
# @File    : chaojiying.py

import requests
from hashlib import md5


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


if __name__ == "__main__":
    chaojiying = Chaojiying_Client('用户名', '密码', '软件ID')  # 用户中心>>软件ID 生成一个替换 96001
    for i in range(3):
        print("第{}次尝试识别".format(i))
        im = open('captcha5.jpg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        print("验证码坐标：")
        json_data = chaojiying.PostPic(im, 1902)
        location_list = []
        print(json_data)
        if json_data["err_no"] == 0:
            print("识别成功！")
            print(json_data["pic_str"])
            break
        else:
            print("识别失败，继续尝试！")
