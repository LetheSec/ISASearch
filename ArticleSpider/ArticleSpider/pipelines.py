# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

# # 同步写入
# class JsonWithEncodingPipeline(object):
#     # #自定义json文件导出将传递进来的item写入文件中的Pipeline
#     def __init__(self):
#         self.file = codecs.open('article.json', 'w', encoding='utf-8')
#
#     # 执行item,将item写入json
#     def process_item(self, item, spider):
#         # 若不加ensure_ascii=False则写入汉字等会出错，直接将unicode写入文件中
#         lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
#         self.file.write(lines)
#         return item
#
#     def spider_closed(self):
#         self.file.close()


# class MysqlPipeline(object):
#     """
#     这样自定义的数据库插入操作，不是异步操作，后续可能会导致插入速度跟不上爬取速度
#     """
#
#     def __init__(self):
#         self.conn = MySQLdb.connect('127.0.0.1', 'root', 'yuan123', 'article_spider', charset='utf8', use_unicode=True)
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         insert_sql = """insert into xianzhi_article(title, create_date, url, url_object_id, front_image_url,
#                         front_image_path, author, view_count, follow_count, mark_count, tags, content)
#                         values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
#         self.cursor.execute(insert_sql, (
#             item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'],
#             item['front_image_path'], item['author'], item['view_count'], item['follow_count'], item['mark_count'],
#             item['tags'], item['content']))
#         self.conn.commit()


# twisted提供异步连接，本身还是用的MysqlDB来连接
class MysqlTwistedPipeline(object):
    # 启动spider时将dbpool传进来
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 该方法会被自动调用可以读取settings的值
    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)  # 可变传参

        return cls(dbpool)  # 实例化本类，启动spider时将dbpool传进来

    def process_item(self, item, spider):
        # 使用twisted将mysql插入编程异步执行,将do_insert变为异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 异常处理

    def handle_error(self, failure):
        # 异常处理,输出异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """insert into xianzhi_article(title, create_date, url, url_object_id, front_image_url, 
                                    front_image_path, author, view_count, follow_count, mark_count, tags, content) 
                                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        # 用的dbpool里取出来的一个cursor进行操作
        cursor.execute(insert_sql, (
            item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'],
            item['front_image_path'], item['author'], item['view_count'], item['follow_count'], item['mark_count'],
            item['tags'], item['content']))


class JsonExporterPipeline(object):
    # 调用Scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 定制图片保存Pipeline
class ArticleImagePipeline(ImagesPipeline):
    # 路径实际上是results[1]里的path
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']  # 保存后的文件路径
        item['front_image_path'] = image_file_path  # 图片本地保存路径
        # 一定要return掉,下一个Pipeline还要用item
        return item
