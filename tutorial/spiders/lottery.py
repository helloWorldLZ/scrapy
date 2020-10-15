# -*- coding: utf-8 -*-
from scrapy.shell import inspect_response
from tutorial.items import Lottery
from tutorial.itemLoaders import LotteryLoader

import scrapy


class LotterySpider(scrapy.Spider):
	name = 'lottery'
	
	custom_settings = {
		'MONGO_DATABASE': 'lottery',
		'LOG_FILE': 'logs/lottery.txt',
		'COLLECTION_NAME': 'ssq'
	}

	def start_requests(self):
		for i in range(128):
			url = 'http://kaijiang.zhcw.com/zhcw/inc/ssq/ssq_wqhg.jsp?pageNum='

			yield scrapy.Request(url=url + str(i+1))

	def parse(self, response):
		tr_elements = response.css('table tr')
		tr_elements = tr_elements[2:-1]		#	去掉表格标题、分页行

		for tr_element in tr_elements:
			l = LotteryLoader(item=Lottery(), selector=tr_element)

			l.add_css('date', 'td:nth-child(1)::text')		#	开奖日期
			l.add_css('issue', 'td:nth-child(2)::text')		#	期号
			l.add_css('red_balls', 'td:nth-child(3) em.rr::text')		#	红球号码
			l.add_css('blue_balls', 'td:nth-child(3) em:last-child::text')		#	篮球号码
			l.add_value('url', response.url)		#	篮球号码

			yield l.load_item()
