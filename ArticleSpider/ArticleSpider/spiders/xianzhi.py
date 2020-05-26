# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse

# from ArticleSpider.items import XianzhiArticleItem
# from ArticleSpider.utils.common import get_md5
from ..items import XianzhiArticleItem
from ..utils.common import get_md5


class XianzhiSpider(scrapy.Spider):
    name = 'xianzhi'  # 启动的时候指定名称
    allowed_domains = ['xz.aliyun.com']
    # start_urls放入要爬取的所有url
    # start_urls = ['https://xz.aliyun.com/tab/13']
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
        article_item = XianzhiArticleItem()
        # 尽量不用完整的xpath路径,因为有的节点是js生成的,但scrapy是爬取静态html页面
        # xpath选择器
        # title = response.xpath(
        #     '//*[@id="Wrapper"]/div/div[1]/div[1]/div/div/div[1]/p/span/text()').extract_first("").strip()
        # create_date = response.xpath('//span[@class="info-left"]/span[2]/text()').extract_first("").strip()
        # view_count = response.xpath('//span[@class="info-left"]/span[4]/text()').extract_first("")[4:].strip()
        # author = response.xpath('//div[@class="topic-info"]/span/a/span/text()').extract_first("").strip()
        # follow_count = response.xpath('//span[@id="follow-count"]/text()').extract_first("").strip()
        # mark_count = response.xpath('//span[@id="mark-count"]/text()').extract_first("").strip()
        # content = response.xpath('//div[@id="topic_content"]').extract_first("")
        # tag_list = response.xpath('//span[@class="content-node"]/span/a/text()').extract()
        # tags = ','.join(tag_list)

        # css选择器
        front_image_url = response.meta.get('front_image_url', '')  # 文章封面图
        title = response.css('.content-title::text').extract_first("")
        create_date = response.css('.info-left span:nth-child(3)::text').extract_first("").strip()
        view_count = response.css('.info-left span:nth-child(5)::text').extract_first("").strip()[4:]
        author = response.css('.info-left span:nth-child(1)::text').extract_first("").strip()
        follow_count = response.css('#follow-count::text').extract_first("").strip()
        mark_count = response.css('#mark-count::text').extract_first("").strip()
        content = response.css('#topic_content').extract_first("")
        tag_list = response.css('.content-node a::text').extract()
        tags = ','.join(tag_list)

        article_item['title'] = title  # 标题
        article_item['url'] = response.url  # url
        article_item['url_object_id'] = get_md5(response.url)  # url的md5
        try:

            create_date = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            create_date = datetime.datetime.now()
        article_item['create_date'] = create_date  # 发布时间
        article_item['view_count'] = view_count  # 浏览量
        article_item['author'] = author  # 作者
        article_item['follow_count'] = follow_count  # 关注数
        article_item['mark_count'] = mark_count  # 收藏数
        article_item['content'] = content  # 文章内容
        article_item['tags'] = tags  # 分类标签(2个)
        article_item['front_image_url'] = [front_image_url]  # 文章图片地址

        yield article_item  # 传递到pipelines
