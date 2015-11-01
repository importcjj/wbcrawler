# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter


class CardPipeline(object):

    def __init__(self):
        self.files = {}

    def process_item(self, item, spider):
        if not item['wb_nick']\
                or not item['wb_location']\
                or not item['wb_images']:
            raise DropItem
        print item['wb_nick'][0]
        item['wb_content'] = ''.join(item['wb_content'])
        item['wb_date'] = item['wb_date'][0]
        item['wb_location'] = item['wb_location'][0]
        images_urls = item.pop('wb_images')
        item['wb_images'] = []
        for image_url in images_urls:
            image_url = image_url.replace('thumbnail', 'large')
            image_url = image_url.replace('square', 'large')
            item['wb_images'].append(image_url)
        self.exporter.export_item(item)
        return item

    def open_spider(self, spider):
        file = open('json/{}_products.json'.format(spider.name), 'w+b')
        self.files[spider] = file
        self.exporter = JsonLinesItemExporter(file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
