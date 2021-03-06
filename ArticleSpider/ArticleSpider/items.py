# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import redis
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Identity
from scrapy.loader import ItemLoader
from .models.es_types import XianzhiArticleType, AnquankeArticleType, SihouArticleType
from w3lib.html import remove_tags
from elasticsearch_dsl.connections import connections
from scrapy.utils.project import get_project_settings

# 连接到es,生成es的实例
xianzhi_es = connections.create_connection(XianzhiArticleType._doc_type.using)
anquanke_es = connections.create_connection(XianzhiArticleType._doc_type.using)
sihou_es = connections.create_connection(XianzhiArticleType._doc_type.using)

# 连接到远程redis服务器
settings = get_project_settings()
redis_cli = redis.StrictRedis(host=settings.get('REDIS_HOST'), password=settings.get('REDIS_PARAMS')['password'])


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        create_date = datetime.datetime.now()
    return create_date


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


# 去除首位空格
def strip(value):
    return value.strip()


def xz_view(value):
    return value[4:]


def gen_suggests(index, info_tuple, es):
    # 根据字符串生成搜索建议数组
    used_words = set()  # 去重
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串,进行分词
            words = es.indices.analyze(index=index, analyzer='ik_max_word', params={'filter': ['lowercase']}, body=text)
            analyzed_words = set([r['token'] for r in words['tokens'] if len(r['token']) > 1])  # 过滤掉只有一个词的
            new_words = analyzed_words - used_words  # 已经存在的词过滤掉
        else:
            new_words = set()

        if new_words:
            suggests.append({'input': list(new_words), 'weight': weight})
    return suggests


class XianzhiArticleItem(scrapy.Item):
    # Item中只有Field类型,可以接收各种数据类型
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(strip, date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    view_count = scrapy.Field(
        input_processor=MapCompose(xz_view)
    )
    author = scrapy.Field()
    follow_count = scrapy.Field()
    mark_count = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(',')
    )
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """INSERT INTO xianzhi_article(title, create_date, url, url_object_id, front_image_url, 
                        front_image_path, author, view_count, follow_count, mark_count, tags, content) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE title=VALUES (title), create_date =VALUES (create_date), 
                        front_image_url = VALUES (front_image_url), front_image_path = VALUES (front_image_path), 
                        author = VALUES (author), view_count = VALUES (view_count), follow_count = VALUES (follow_count),
                        mark_count = VALUES (mark_count), tags = VALUES (tags), content = VALUES (content)"""
        params = (
            self.get('title', ''),
            self.get('create_date', '0000-00-00 00:00:00'),
            self.get('url', ''),
            self.get('url_object_id', ''),
            self.get('front_image_url', ''),
            self.get('front_image_path', ''),
            self.get('author', ''),
            self.get('view_count', '0'),
            self.get('follow_count', '0'),
            self.get('mark_count', '0'),
            self.get('tags', ''),
            self.get('content', '')
        )
        return insert_sql, params

    def save_to_es(self):
        article = XianzhiArticleType()
        article.title = self.get('title', '')
        article.author = self.get('author', '')
        article.create_date = self.get('create_date', '0000-00-00 00:00:00')
        article.content = remove_tags(self.get('content', ''))
        article.front_image_url = self['front_image_url']
        if 'front_image_path' in self:
            article.front_image_path = self.get('front_image_path', '')
        article.view_count = self.get('view_count', '0')
        article.comment_count = self.get('comment_count', '0')
        article.mark_count = self.get('mark_count', '0')
        article.url = self.get('url', '')
        article.tags = self.get('tags', '')
        article.meta.id = self.get('url_object_id', '')
        article.suggest = gen_suggests(XianzhiArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)),
                                       xianzhi_es)
        article.save()
        redis_cli.incr("xianzhi_count")
        return


class AnquankeArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(strip, date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    author = scrapy.Field()
    view_count = scrapy.Field()
    comment_count = scrapy.Field()
    like_count = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(',')
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """INSERT INTO anquanke_article(title, create_date, url, url_object_id, front_image_url, 
                        front_image_path, author, view_count, comment_count, like_count, tags, content) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE title=VALUES (title), create_date =VALUES (create_date), 
                        front_image_url = VALUES (front_image_url), front_image_path = VALUES (front_image_path), 
                        author = VALUES (author), view_count = VALUES (view_count), comment_count = VALUES (comment_count),
                        like_count = VALUES (like_count), tags = VALUES (tags), content = VALUES (content)"""
        params = (
            self.get('title', ''),
            self.get('create_date', '0000-00-00 00:00:00'),
            self.get('url', ''),
            self.get('url_object_id', ''),
            self.get('front_image_url', ''),
            self.get('front_image_path', ''),
            self.get('author', ''),
            self.get('view_count', '0'),
            self.get('comment_count', '0'),
            self.get('like_count', '0'),
            self.get('tags', ''),
            self.get('content', '')
        )

        return insert_sql, params

    def save_to_es(self):
        article = AnquankeArticleType()
        article.title = self.get('title', '')
        article.author = self.get('author', '')
        article.create_date = self.get('create_date', '0000-00-00 00:00:00')
        article.content = remove_tags(self.get('content', ''))
        article.front_image_url = self['front_image_url']
        if 'front_image_path' in self:
            article.front_image_path = self.get('front_image_path', '')
        article.view_count = self.get('view_count', '0')
        article.comment_count = self.get('comment_count', '0')
        article.like_count = self.get('like_count', '0')
        article.url = self.get('url', '')
        article.tags = self.get('tags', '')
        article.meta.id = self.get('url_object_id', '')
        # 生成搜索建议词
        article.suggest = gen_suggests(AnquankeArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)),
                                       anquanke_es)
        article.save()
        redis_cli.incr("anquanke_count")
        return


class SihouArticleItem(scrapy.Item):
    # Item中只有Field类型,可以接收各种数据类型
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(strip, date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    view_count = scrapy.Field()
    author = scrapy.Field()
    praise_count = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=Join(',')
    )
    front_image_url = scrapy.Field(
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """INSERT INTO sihou_article(title, create_date, url, url_object_id, front_image_url, 
                        front_image_path, author, view_count, praise_count, tags, content) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE title=VALUES (title), create_date =VALUES (create_date), 
                        front_image_url = VALUES (front_image_url), front_image_path = VALUES (front_image_path), 
                        author = VALUES (author), view_count = VALUES (view_count), praise_count = VALUES (praise_count),
                        tags = VALUES (tags), content = VALUES (content)"""
        params = (
            self.get('title', ''),
            self.get('create_date', '0000-00-00 00:00:00'),
            self.get('url', ''),
            self.get('url_object_id', ''),
            self.get('front_image_url', ''),
            self.get('front_image_path', ''),
            self.get('author', ''),
            self.get('view_count', '0'),
            self.get('praise_count', '0'),
            self.get('tags', ''),
            self.get('content', '')
        )
        return insert_sql, params

    def save_to_es(self):
        article = SihouArticleType()
        article.title = self.get('title', '')
        article.author = self.get('author', '')
        article.create_date = self.get('create_date', '0000-00-00 00:00:00')
        article.content = remove_tags(self.get('content', ''))
        article.front_image_url = self['front_image_url']
        if 'front_image_path' in self:
            article.front_image_path = self.get('front_image_path', '')
        article.view_count = self.get('view_count', '0')
        article.praise_count = self.get('praise_count', '0')
        article.url = self.get('url', '')
        article.tags = self.get('tags', '')
        article.meta.id = self.get('url_object_id', '')
        article.suggest = gen_suggests(SihouArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)),
                                       sihou_es)
        article.save()
        redis_cli.incr("sihou_count")
        return
