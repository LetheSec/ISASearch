# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


# 定制图片保存Pipeline
class ArticleImagePipeline(ImagesPipeline):
    # 路径实际上是results[1]里的path
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']     # 保存后的文件路径
        item['front_image_path'] = image_file_path  # 图片本地保存路径
        # 一定要return掉,下一个Pipeline还要用item
        return item
