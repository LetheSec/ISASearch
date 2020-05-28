# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse

from ..items import XianzhiArticleItem, ArticleItemLoader
from ..utils.common import get_md5


class XianzhiSpider(scrapy.Spider):
    name = 'xianzhi'  # 启动的时候指定名称
    allowed_domains = ['xz.aliyun.com']
    # start_urls放入要爬取的所有url
    start_urls = ['https://xz.aliyun.com/tab/13']

    #
    start_urls = ['https://xz.aliyun.com/tab/4', 'https://xz.aliyun.com/tab/1', 'https://xz.aliyun.com/tab/9',
                  'https://xz.aliyun.com/tab/13', 'https://xz.aliyun.com/tab/10', 'https://xz.aliyun.com/tab/7']

    # 爬取的每个url会进入这个函数，会返回response
    def parse(self, response):
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.css('table.table.topic-list tr')
        for post_node in post_nodes:
            image_url = post_node.css('a.user-link img::attr(src)').extract_first()  # 图片地址
            post_url = post_node.css('a.topic-title::attr(href)').extract_first()
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy下载
        next_url = response.css('div.pagination.clearfix li:nth-child(3) a::attr(href)').extract_first("")
        if next_url and next_url.startswith('?'):
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):

        # 通过item_loader加载item
        item_loader = ArticleItemLoader(item=XianzhiArticleItem(), response=response)
        item_loader.add_value('front_image_url', [response.meta.get('front_image_url', '')])
        item_loader.add_css('title', '.content-title::text')  # 添加css选择器
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('create_date', '.info-left span:nth-child(3)::text')
        item_loader.add_css('view_count', '.info-left span:nth-child(5)::text')
        item_loader.add_css('author', '.info-left span:nth-child(1)::text')
        item_loader.add_css('follow_count', '#follow-count::text')
        item_loader.add_css('mark_count', '#mark-count::text')
        item_loader.add_css('content', '#topic_content')
        item_loader.add_css('tags', '.content-node a::text')

        article_item = item_loader.load_item()

        yield article_item  # 传递到pipelines
