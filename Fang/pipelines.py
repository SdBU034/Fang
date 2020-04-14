# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.exporters import JsonLinesItemExporter

class FangPipeline(object):
    newhouse_fp = open('new_house.json', 'wb')
    esf_fp = open('esf.json', 'wb')
    newhouse_exporter = JsonLinesItemExporter(newhouse_fp, ensure_ascii=False)
    esf_exporter = JsonLinesItemExporter(esf_fp, ensure_ascii=False)

    def process_item(self, item, spider):
        # 写入到本地json文件
        self.newhouse_exporter.export_item(item)
        self.esf_exporter.export_item(item)


        # 保存到mysql数据库
        # self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='******', database='******', charset='utf8')
        # sql = "INSERT INTO tb_fang (province,city,name,rooms,area,price,district,address,status,origin_url) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        # with self.conn.cursor() as cursor:
        #     cursor.execute(sql,(item['province'],item['city'],item['name'],item['rooms'],item['area'],item['price'],item['district'],item['address'],item['status'],item['origin_url']))
        # self.conn.commit()
        return item

