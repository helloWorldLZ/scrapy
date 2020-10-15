# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash
import time
import re
import json

from scrapy.shell import inspect_response
from tutorial.items import Product
from tutorial.itemLoaders import ProductLoader


class CameraSpider(scrapy.Spider):
    name = 'camera'

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
            'url': 'https://search.jd.com/Search?keyword=手机&enc=utf-8&wq=手机&pvid=5b3e800e664c43869c8a72e46929024e',
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
        isOk = self.checkPageIndex(response)    # 有的时候偶现不一致的情况
        if not isOk:
            return

        urls = response.css('li.gl-item div.p-name a::attr(href)').getall()
        pageNum = response.meta['pageNum']
        # self.save2file(urls, pageNum)    # 运行 getLostProduct.py 查询丢失的 item

        script = '''
        function main(splash, args)
            splash.images_enabled = false
            splash:go(args.url)
            splash:wait(8)

            return splash:html()
        end
        '''

        argsDict = {
            'url': '',
            'lua_source': script,
        }

        # urls = [
        #     "https://item.jd.com/46004969194.html",
        #     "https://item.jd.com/23474069715.html",
        # ]

        for url in urls:
            if not url.startswith('https:'):
                url = 'https:' + url

            # argsDict['url'] = 'https://item.jd.com/7509313.html'  # 32页评论
            argsDict['url'] = url

            yield scrapy_splash.SplashRequest(
                url, self.parseProduct, args=argsDict, endpoint='execute', priority=1,
                meta={
                    'pageNum': pageNum
                }
            )

            # break

    def checkPageIndex(self, response):
        isOk = True

        pageNum = response.meta['pageNum']
        curPageNum = response.css('#J_bottomPage .p-num a.curr::text').get()

        if pageNum != int(curPageNum):
            message = '===== pageNum: %s  curPageNum: %s  =====' % (pageNum, curPageNum)
            self.logger.info(message)
            isOk = False

        return isOk

    def save2file(self, urls, pageNum):
        fileName = 'logs/urls{}.json'.format(pageNum)
        with open(fileName, 'w') as f_obj:   # 可以用来查询未爬取到的 item
            json.dump(urls, f_obj, indent=4)

    def parseProduct(self, response):
        urls = response.css('#spec-list li img::attr(src)').getall()

        productLoader = self.getLoader(response)

        meta = {
            'l': productLoader,
            'imgs': [x for x in range(len(urls))],
            'referer': response.url,    # 评论接口要用
        }

        for url in urls:
            url = self.checkImgUrl(url)

            yield scrapy.Request(url=url, callback=self.parseImgs, meta=meta, dont_filter=True)

        # return productLoader.load_item()

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

        # l.add_css('image_urls', '#spec-list li img::attr(src)')

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

    def checkImgUrl(self, url):
        url = url.replace('54x54', '450x450')
        url = url.replace('75x75', '450x450')

        index = url.find('/jfs/')
        if index > 0:
            url = url.replace('/jfs/', '/s450x450_jfs/')

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
        with open(filename, 'wb') as f:
            f.write(response.body)

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

        # 请求第一页评论数据，从响应结果中获取 maxPage，循环获取剩余页码中的评论
        url = 'https://sclub.jd.com/comment/productPageComments.action?score=0&sortType=5&pageSize=10&isShadowSku=0&rid=0&fold=1&productId={}&page='
        baseUrl = url.format(productId)

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
