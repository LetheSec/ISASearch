# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from ..items import ArticleItemLoader, SihouArticleItem
from ..utils.common import get_md5


class A4houSpider(scrapy.Spider):
    name = 'sihou'
    allowed_domains = ['4hou.com']
    start_urls = ['https://www.4hou.com']

    # 爬取的每个url会进入这个函数，会返回response
    def parse(self, response):
        # types = response.css('div.technology a::attr(href)').extract()
        for type_url in response.css('div.technology a::attr(href)').extract():
            for i in range(1, 150):
                page = "?page={}".format(i)
                yield Request(url=type_url + page, callback=self.parse_post)

    def parse_post(self, response):
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        if response.css('div.main-box') != []:
            post_nodes = response.css('div.main-box')
            for post_node in post_nodes:
                image_url = post_node.css('div.new_img img::attr(src)').extract_first()  # 图片地址
                view_count = post_node.css('div.read span::text').extract_first().replace(',', '')  # 浏览量
                praise_count = post_node.css('div.Praise span::text').extract_first().replace(',', '')  # 点赞数
                post_url = post_node.css('div.new_con a::attr(href)').extract_first()
                yield Request(url=post_url,
                              meta={'front_image_url': image_url, 'view_count': view_count,
                                    'praise_count': praise_count},
                              callback=self.parse_detail)

    def parse_detail(self, response):
        # 通过item_loader加载item

        item_loader = ArticleItemLoader(item=SihouArticleItem(), response=response)
        item_loader.add_value('front_image_url', [response.meta.get('front_image_url', '')])
        item_loader.add_css('title', 'h1.art_title::text')  # 添加css选择器
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('create_date', 'div.art_time span:nth-child(3)::text')
        item_loader.add_value('view_count', response.meta.get('view_count', '0'))
        item_loader.add_css('author', 'span.sir::text')
        item_loader.add_value('praise_count', response.meta.get('praise_count', '0'))
        item_loader.add_css('content', 'div.article_cen')
        item_loader.add_css('tags', 'span.lei::text')

        article_item = item_loader.load_item()

        yield article_item  # 传递到pipelines
