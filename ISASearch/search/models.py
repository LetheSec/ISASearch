from django.db import models

# Create your models here.

# -*- coding: utf-8 -*-
# @Time    : 2020/6/1 11:53
# @Author  : Yuan.XJ
# @File    : es_types.py


from elasticsearch_dsl import DocType, Date, Keyword, Text, Integer, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer  as _CustomAnalyzer

connections.create_connection(hosts=['localhost'])


# 自定义analyzer,为了防止报错
class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer('ik_max_word', filter=['lowercase'])  # filter大小写转换


class XianzhiArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer='ik_max_word')
    author = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    view_count = Integer()
    follow_count = Integer()
    mark_count = Integer()
    front_image_url = Keyword()
    front_image_path = Keyword()
    tags = Text(analyzer='ik_max_word')
    content = Text(analyzer='ik_max_word')

    class Meta:
        index = 'xianzhi'
        doc_type = 'xianzhi_article'


class AnquankeArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer='ik_max_word')
    author = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    view_count = Integer()
    comment_count = Integer()
    like_count = Integer()
    front_image_url = Keyword()
    front_image_path = Keyword()
    tags = Text(analyzer='ik_max_word')
    content = Text(analyzer='ik_max_word')

    class Meta:
        index = 'anquanke'
        doc_type = 'anquanke_article'


class SihouArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer='ik_max_word')
    author = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    view_count = Integer()
    praise_count = Integer()
    front_image_url = Keyword()
    front_image_path = Keyword()
    tags = Text(analyzer='ik_max_word')
    content = Text(analyzer='ik_max_word')

    class Meta:
        index = 'sihou'
        doc_type = 'sihou_article'


if __name__ == '__main__':
    # 先运行此类来生成mapping
    XianzhiArticleType.init()
    AnquankeArticleType.init()
    SihouArticleType.init()
