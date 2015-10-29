# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WbcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WeiboCard(scrapy.Item):
    wb_nick = scrapy.Field()
    wb_date = scrapy.Field()
    wb_content = scrapy.Field()
    wb_images = scrapy.Field()
    wb_coordinate = scrapy.Field()
    wb_location = scrapy.Field()
