# -*- coding:utf-8 -*-
import json
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from wbcrawler.items import WeiboCard
from scrapy.exceptions import IgnoreRequest
from wbcrawler.settings import WEIBO_ACCOUNT
from wbcrawler.utils.login import (
    WeiboLoginer,
    LoginFailed
)


weibos_re = r'<script>STK && STK.pageletM && STK.pageletM.view\(({"pid":"pl_w'\
    'eibo_direct".*?})\)</script>'


class SimpleSpider(scrapy.spiders.Spider):

    name = "simple"
    allowed_domains = ['weibo.com']
    url_prefix = u'http://s.weibo.com/'
    search_url = u'weibo/%E4%B8%AD%E5%B1%B1%E9%99%B5&typeall'\
        '=1&suball=1&page={}&scope=ori&haspic=1'

    def start_requests(self):
        """
        """
        loginer = WeiboLoginer(**WEIBO_ACCOUNT)
        loginer.easy_login()
        self.cookies = [c.__dict__ for c in loginer.cookie]
        start_url = ''.join([self.url_prefix, self.search_url.format(1)])
        return [Request(url=start_url,
                        cookies=self.cookies,
                        meta={'cookiejar': 1})]

    def parse(self, response):
        sel = Selector(response)
        try:
            page_json = sel.re(weibos_re)[0]
        except IndexError:
            raise LoginFailed()
        page_html = json.loads(page_json).get('html')
        if not page_html:
            raise IgnoreRequest()
        page_urls = Selector(text=page_html).xpath(
            './/a[contains(@suda-data,"key=tblog_search_weibo&value=weibo_page'
            '")]/@href'
        ).extract()
        page_urls.pop(-1)
        page_urls.append(self.search_url.format(1))
        for href in page_urls:
            url = ''.join([self.url_prefix, href])
            yield Request(url=url,
                          meta={'cookiejar': 1},
                          cookies=self.cookies,
                          callback=self.parse_weibo)

    def parse_weibo(self, response):
        sel = Selector(response)
        weibos_json = sel.re(weibos_re)[0]
        weibos_html = json.loads(weibos_json).get('html')
        if not weibos_html:
            raise IgnoreRequest()
        wb_cards = Selector(text=weibos_html).xpath(
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
            item['wb_location_url'] = card.xpath(
                './/a[@class="W_btn_c6"]/@href').extract()
            item['wb_location'] = card.xpath(
                './/span[@class="W_btn_tag"]/@title').extract()
            yield item
