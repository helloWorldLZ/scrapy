import scrapy
import scrapy_splash
import re

from scrapy.shell import inspect_response
from tutorial.items import Product
from tutorial.itemLoaders import ProductLoader


class LaptopSpider(scrapy.Spider):
    name = 'laptop'

    def start_requests(self):
        script = '''
        function main(splash, args)
            splash.images_enabled = false
            splash:go(args.url)
            splash:wait(args.wait)

            splash:select('#J_bottomPage input.input-txt'):setAttribute('value', args.pageNum)
            splash:select('#J_bottomPage .p-skip a'):mouse_click()
            splash:wait(args.wait)

            splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
            splash:wait(args.wait)

            return splash:html()
        end
        '''

        argsDict = {
            'url': 'https://search.jd.com/Search?keyword=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&enc=utf-8&wq=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&pvid=ac1a66343dcb4d5d968f2364129db367',
            'wait': 6,
            'pageNum': 1,
            'lua_source': script,
        }

        # 使用的 virtualbox 虚拟机，性能有限，一次爬10页，手动搜索看到一共有100页
        for i in range(10):
            yield scrapy_splash.SplashRequest(
                argsDict['url'], self.parse, args=argsDict, endpoint='execute', priority=2,
                meta={
                    'pageNum': argsDict['pageNum']
                }
            )

            argsDict['pageNum'] += 1
            # break

    def parse(self, response):
        urls = response.css('li.gl-item div.p-name a::attr(href)').getall()
        pageNum = response.meta['pageNum']

        script = '''
        function main(splash, args)
            splash.images_enabled = false
            splash:go(args.url)
            splash:wait(6)

            return splash:html()
        end
        '''

        argsDict = {
            'url': '',
            'lua_source': script,
        }

        for url in urls:
            if not url.startswith('https:'):
                url = 'https:' + url

            argsDict['url'] = url

            yield scrapy_splash.SplashRequest(
                url, self.parseProduct, args=argsDict, endpoint='execute', priority=1,
                meta={
                    'pageNum': pageNum
                }
            )

    def parseProduct(self, response):
        productLoader = self.getLoader(response)

        yield productLoader.load_item()

    def getLoader(self, response):
        productId = re.sub(r'\D', '', response.url)

        l = ProductLoader(item=Product(), response=response)

        l.add_css('name', '.itemInfo-wrap .sku-name::text')
        l.add_css('price', '.itemInfo-wrap .summary-price-wrap .p-price .price::text')
        l.add_value('url', response.url)
        l.add_value('productId', productId)
        l.add_css('shopName', '#crumb-wrap .item .name a::text')
        l.add_css('shopUrl', '#crumb-wrap .item .name a::attr(href)')

        l.add_css('brand', '#parameter-brand li a::text')
        l.add_css('parameterList', '#detail .p-parameter .parameter2 li::text')
        l.add_css('packageList', '#detail .tab-con .package-list *::text')

        l.add_value('pageNum', response.meta['pageNum'])

        for table_item in response.css('#detail .tab-con .Ptable-item'):
            tableDic = {
                'tableName': table_item.css('h3::text').get(),
                'dlItems': []
            }

            for dl in table_item.css('dl dl'):
                tableDic['dlItems'].append([
                    dl.css('dt::text').get(),
                    dl.css('dd:last-child::text').get(),
                ])

            l.add_value('tableItem', tableDic)

        return l
