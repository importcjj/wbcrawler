# -*- coding:utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.exceptions import IgnoreRequest
from scrapy.http import Request
from wbcrawler.items import WeiboCard
import json


RE_PATTREN = r'<script>STK && STK.pageletM && STK.pageletM.view\(({"pid":"pl_weibo_direct".*?})\)</script>'


class SimpleSpider(scrapy.spiders.Spider):

    name = "simple"
    allowed_domains = ['weibo.com']
    start_urls = [
        'http://s.weibo.com/weibo/'
        '%E4%B8%AD%E5%B1%B1%E9%99%B5&typeall=1&suball=1&page=1'
    ]

    def parse(self, response):
        sel = Selector(response)
        json_text = sel.re(RE_PATTREN)[0]
        html_code = json.loads(json_text).get('html')
        if not html_code:
            raise IgnoreRequest()
        total = Selector(text=html_code).xpath(
            './/a[@suda-data="key=tblog_search_weibo&value=weibo_page"]/text()').extract()
        print total

        for page_id in xrange(1, total + 1):
            yield Request(url=search_url.format(page_id), callable=parse_card)

    def parse_card(self, response):
        sel = Selector(response)
        json_text = sel.re(RE_PATTREN)[0]
        html_code = json.loads(json_text).get('html')
        if not html_code:
            raise IgnoreRequest()
        wb_cards = Selector(text=html_code).xpath(
            '//div[contains(@class, "WB_card")]')
        for card in wb_cards:
            item = WeiboCard()
            item['wb_nick'] = card.xpath(
                './/a[contains(@class, "W_texta W_fb")]/text()').extract()
            item['wb_content'] = card.xpath(
                './/p[@class="comment_txt"]/text()').extract()
            item['wb_images'] = card.xpath(
                './/img[@action-data]/@src').extract()
            item['wb_date'] = card.xpath(
                './/a[@node-type="feed_list_item_date"]/@date').extract()
            item['wb_location'] = card.xpath(
                './/span[@class="W_btn_tag"]/@title').extract()
            yield item
