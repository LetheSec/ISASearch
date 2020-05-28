# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.http import Request
from ..items import AnquankeArticleItem, ArticleItemLoader
from ..utils.common import get_md5


class AnquankeSpider(scrapy.Spider):
    name = 'anquanke'
    allowed_domains = ['api.anquanke.com', 'anquanke.com']
    start_urls = ['https://api.anquanke.com/data/v1/posts?size=500']

    def parse(self, response):
        res = json.loads(response.text)
        posts = res.get('data')
        for post in posts:
            # 剔除掉活动和招聘的文章
            if ('招聘' in post.get('tags')) or ('活动' in post.get('tags')):
                continue
            item_loader = ArticleItemLoader(item=AnquankeArticleItem(), response=response)
            item_loader.add_value('title', post.get('title'))
            item_loader.add_value('create_date', post.get('date'))
            item_loader.add_value('front_image_url', post.get('cover'))
            item_loader.add_value('author', post.get('author').get('nickname'))
            item_loader.add_value('view_count', post.get('pv'))
            item_loader.add_value('comment_count', post.get('comment'))
            item_loader.add_value('like_count', post.get('like_count'))
            item_loader.add_value('tags', post.get('tags'))
            yield Request(url='https://www.anquanke.com/post/id/{}'.format(post.get('id')),
                          meta={'article_item': item_loader}, callback=self.parse_content)
        # 获取下一页
        next_url = res.get('next')
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_content(self, response):
        item_loader = response.meta.get('article_item', '')
        content = response.css('div.article-content').extract_first().replace('data-original=', 'src=')
        item_loader.add_value('content', content)
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))

        article_item = item_loader.load_item()
        yield article_item
