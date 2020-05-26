# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class XianzhiArticleItem(scrapy.Item):
    # Item中只有Field类型,可以接收各种数据类型
    url = scrapy.Field()
    url_object_id = scrapy.Field()  # url的md5
    title = scrapy.Field()
    create_date = scrapy.Field()
    view_count = scrapy.Field()
    author = scrapy.Field()
    follow_count = scrapy.Field()
    mark_count = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
