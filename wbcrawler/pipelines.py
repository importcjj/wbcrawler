# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem


class CardPipeline(object):

    def process_item(self, item, spider):
        if not item['wb_nick']\
                or not item['wb_location']\
                or not item['wb_images']:
            raise DropItem
        item['wb_content'] = ''.join(item['wb_content'])
        item['wb_date'] = item['wb_date'][0]
        item['wb_location'] = item['wb_location'][0]
        return item
