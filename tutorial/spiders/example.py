# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash
import json

from scrapy.shell import inspect_response

class ExampleSpider(scrapy.Spider):
	name = 'example'

	def start_requests(self):
		script = '''
		function main(splash, args)
			splash.images_enabled = false
			splash:go(args.url)
			splash:wait(args.wait)

			return splash:html()
		end
		'''

		argsDict = {
			'url': 'http://www.zjwjw.gov.cn/col/col1202101/index.html',
			'wait': 5,
			'lua_source': script,
		}

		yield scrapy_splash.SplashRequest(
			argsDict['url'], self.parse, args=argsDict, endpoint='execute'
		)

	def parse(self, response):
		inspect_response(response, self)

		response.css('#4978845 .default_pgContainer li')
