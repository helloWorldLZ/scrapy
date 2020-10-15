# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash

# from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader
from tutorial.items import Product
from tutorial.itemLoaders import ProductLoader


class CameraIndexSpider(scrapy.Spider):
    name = 'cameraIndex'
    # start_urls = [
    #     'file:///D:/liuzhe/PycharmProjects/scrapy3_learning/temp.html'
    # ]

    def start_requests(self):

        script = '''
        function main(splash, args)
            splash.images_enabled = false
            splash:go(args.url)
            splash:wait(2)

            splash:select('#key'):send_text('数码相机')
            splash:select('#search button'):mouse_click()
            splash:wait(8)

            splash:select('#J_bottomPage input.input-txt'):setAttribute('value', args.pageNum)
            splash:select('#J_bottomPage .p-skip a'):mouse_click()
            splash:wait(args.wait)

            splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
            splash:wait(args.wait)

            return splash:html()
        end
        '''

        argsDict = {
            'url': 'https://www.jd.com',
            'wait': 5,
            'pageNum': 1,
            'lua_source': script,
        }

        # 使用的 virtualbox 虚拟机，性能有限，一次爬10页，手动搜索看到一共有100页
        for i in range(10):
            yield scrapy_splash.SplashRequest(
                argsDict['url'], self.parse, args=argsDict, endpoint='execute', 
                meta={
                    'pageNum': argsDict['pageNum']
                }
            )

            argsDict['pageNum'] += 1


    def parse(self, response):
        gl_items = response.css('li.gl-item')

        #   调试代码
        pageNum = response.meta['pageNum']
        curPageNum = response.css('#J_bottomPage .p-num a.curr::text').get()
        message = '===== pageNum: %s  curPageNum: %s  itemLen: %s =====' % (pageNum, curPageNum, len(gl_items))
        self.logger.info(message)
        
        for gl_item in gl_items:
            if len(gl_item.css('div.gl-i-tab')) == 0:   #   如果 len() 返回 1，说明含有页签，html 结构不一样
                yield self.getProduct(gl_item)
            else:
                for tab_content_item in gl_item.css('div.tab-content-item'):
                    yield self.getProduct(tab_content_item)


    def getProduct(self, selector):
        l = ProductLoader(item=Product(), selector=selector)

        l.add_css('name', 'div.p-name em *::text')
        l.add_css('price', 'div.p-price strong i::text')
        # l.add_css('plusPrice', 'div.p-price span.price-plus-1 em::text')
        l.add_css('url', 'div.p-name a::attr(href)')
        l.add_css('shopName', 'div.p-shop a::text')
        l.add_css('shopUrl', 'div.p-shop a::attr(href)')

        return l.load_item()


    def parseTest(self, response):
        # inspect_response(response, self)

        pageNum = response.css('#J_bottomPage .p-num a.curr::text').get()
        filename = 'temp{}.html'.format(pageNum)
        with open(filename, 'wb') as f:
            f.write(response.body)


        for gl_item in response.css('li.gl-item'):
            print(gl_item.css('div.p-name a::attr(href)').get())


