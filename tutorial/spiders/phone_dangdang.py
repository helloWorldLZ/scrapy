# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash
import time
import re
import json

from scrapy.shell import inspect_response
from tutorial.items import Product
from tutorial.itemLoaders import DangdangLoader


class PhoneDangdangSpider(scrapy.Spider):
    name = 'phone_dangdang'

    def start_requests(self):
        script = '''
        function main(splash, args)
            splash.images_enabled = false
            splash:go(args.url)
            splash:wait(args.wait)
            
            splash:select('#t__cp'):setAttribute('value', args.pageNum)
            splash:select('#click_get_page'):mouse_click()
            splash:wait(args.wait)

            return splash:html()
        end
        '''

        argsDict = {
            'url': r'http://search.dangdang.com/?key=%CA%D6%BB%FA&act=input&page_index=1',
            'wait': 3.9,
            'pageNum': 1,
            'lua_source': script,
        }

        # 使用的 virtualbox 虚拟机，性能有限，一次爬10页，手动搜索看到一共有100页
        for i in range(5):
            yield scrapy_splash.SplashRequest(
                argsDict['url'], self.parse, args=argsDict, endpoint='execute', priority=2,
                meta={
                    'pageNum': argsDict['pageNum']
                }
            )

            argsDict['pageNum'] += 1
            # break

    def parse(self, response):
        # inspect_response(response, self)
        urls = response.css('#component_59 li .name a::attr(href)').getall()
        pageNum = response.meta['pageNum']

        script = '''
        function main(splash, args)
            splash.images_enabled = false
            splash:go(args.url)
            splash:wait(5)

            splash:runjs("window.scrollTo(0, document.body.scrollHeight);")

            return splash:html()
        end
        '''

        argsDict = {
            'url': '',
            'lua_source': script,
        }

        for url in urls:
            argsDict['url'] = url

            yield scrapy_splash.SplashRequest(
                url, self.parseProduct, args=argsDict, endpoint='execute', priority=1,
                meta={
                    'pageNum': pageNum
                }
            )
            # break

    def parseProduct(self, response):
        productLoader = self.getLoader(response)

        yield productLoader.load_item()

    def getLoader(self, response):
        productId = re.sub(r'\D', '', response.url)

        l = DangdangLoader(item=Product(), response=response)

        l.add_css('name', '#product_info h1::text')
        l.add_css('price', '#dd-price::text')
        l.add_value('url', response.url)
        l.add_value('productId', productId)
        l.add_css('shopName', '#service-more .title_name a::text')
        l.add_css('shopUrl', '#service-more .title_name a::attr(href)')
        l.add_css('brand', '#breadcrumb span:nth-child(5)::text')
        l.add_value('pageNum', response.meta['pageNum'])
        
        for li_item in response.css('#detail_describe li'):
        	txts = li_item.css('::text').getall()

        	l.add_value('parameterList', [txts])

        return l

    def checkImgUrl(self, url):
        if not url.startswith('https:'):
            url = 'https:' + url
        
        return url

    def parseImgs(self, response):
        meta = response.meta
        productLoader = meta['l']
        imgs = meta['imgs']

        productId = productLoader.get_output_value('productId')
        picNo = len(imgs)

        url = response.url
        start = url.rindex('.')
        fileType = url[start:]

        filename = 'imgs/{}_{}{}'.format(productId, picNo, fileType)
        # with open(filename, 'wb') as f:
        #     f.write(response.body)

        img = {
            'b': response.body,
            'path': filename,
        }

        productLoader.add_value('imgs', img)

        imgs.pop()
        if len(imgs) == 0:
            yield self.crawlCommentsPage0(meta)

    def crawlCommentsPage0(self, meta):
        productLoader = meta['l']
        productId = productLoader.get_output_value('productId')
        commentVersion = meta['commentVersion']

        # 请求第一页评论数据，从响应结果中获取 maxPage，循环获取剩余页码中的评论
        url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv{}&score=0&sortType=5&pageSize=10&isShadowSku=0&rid=0&fold=1&productId={}&page='
        baseUrl = url.format(commentVersion, productId)

        headers = {'referer': meta['referer']}
        metaDic = {
            'l': productLoader,
            'baseUrl': baseUrl,
            'referer': meta['referer'],
        }

        return scrapy.Request(url=baseUrl + '0', callback=self.parseCommentsPage0, headers=headers, meta=metaDic)

    def parseCommentsPage0(self, response):
        meta = response.meta
        productLoader = meta['l']
        baseUrl = meta['baseUrl']
        headers = {'referer': meta['referer']}

        result = self.getResult(response)
        maxPage = result['maxPage']

        self.addComments(result['comments'], productLoader)		# 没有评论时， comments 是 []

        # 没有评论 或者 只有一页评论
        if maxPage < 2:
            yield productLoader.load_item()
            return

        metaDic = {
            'l': productLoader,
            'tryTimes': [0],
        }

        for i in range(maxPage):
            if i == 0:
                continue

            url = baseUrl + str(i)

            yield scrapy.Request(url=url, callback=self.parseComments, headers=headers, meta=metaDic)

    def getResult(self, response):
        text = response.text

        if text.startswith('fetchJSON'):
            start = text.index('{')
            text = text[start:-2]   # 截取 fetchJSON_comment98vv123( 和 ); 中间的 json 字符串

        result = json.loads(text)

        return result

    def addComments(self, comments, productLoader):
        for comment in comments:
            commentDic = {
                'content': comment['content'],
                'creationTime': comment['creationTime'],
            }

            # 判断是否有追评
            if comment['afterDays'] > 0 and 'afterUserComment' in comment:
                afterUserComment = comment['afterUserComment']

                commentDic['afterContent'] = afterUserComment['content']
                commentDic['afterCreated'] = afterUserComment['created']
                commentDic['afterDays'] = comment['afterDays']

            productLoader.add_value('comments', commentDic)

    def parseComments(self, response):
        productLoader = response.meta['l']

        result = self.getResult(response)
        self.addComments(result['comments'], productLoader)

        maxPage = result['maxPage']
        tryTimes = response.meta['tryTimes']
        tryTimes.append(0)

        if maxPage == len(tryTimes):
            yield productLoader.load_item()

