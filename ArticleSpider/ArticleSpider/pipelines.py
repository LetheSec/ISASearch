# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


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
            charset='utf8mb4',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)  # 可变传参

        return cls(dbpool)  # 实例化本类，启动spider时将dbpool传进来

    def process_item(self, item, spider):
        # 使用twisted将mysql插入编程异步执行,将do_insert变为异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 异常处理
        return item

    def handle_error(self, failure):
        # 异常处理,输出异常
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)



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
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']  # 保存后的文件路径
            item['front_image_path'] = image_file_path  # 图片本地保存路径
        # 一定要return掉,下一个Pipeline还要用item
        return item


class ElasticsearchPipeline(object):
    # 将数据写入es中
    def process_item(self, item, spider):
        # 将item转换为es的数据
        item.save_to_es()
