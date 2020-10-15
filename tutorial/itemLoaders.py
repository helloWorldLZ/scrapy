# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity

def trip(value):
	value = value.strip()
	res = value if value != '' else None

	return res

def checkUrl(url):
	if not url.startswith('https:'):
		url = 'https:' + url
			
	return url

def changeSize(url):
	return url.replace('54x54', '450x450')

class ProductLoader(ItemLoader):
	default_output_processor = TakeFirst()

	name_in = MapCompose(str.strip)
	shopUrl_in = MapCompose(checkUrl)
	# image_urls_in = MapCompose(checkUrl, changeSize)

	parameterList_out = Identity()
	tableItem_out = Identity()
	packageList_out = MapCompose(trip)
	comments_out = Identity()
	# image_urls_out = Identity()
	# images_out = Identity()
	imgs_out = Identity()

class DangdangLoader(ItemLoader):
	default_output_processor = TakeFirst()

	name_in = MapCompose(str.strip)
	
	parameterList_out = Identity()

class LotteryLoader(ItemLoader):
	default_output_processor = TakeFirst()

	red_balls_out = Identity()
