# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join, Identity
from scrapy.loader import ItemLoader


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


class XianzhiArticleItem(scrapy.Item):
    # Item中只有Field类型,可以接收各种数据类型
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(strip, date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field()
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
