# -*- coding: utf-8 -*-
import scrapy
import scrapy_splash
import time
import re
import json

from scrapy.shell import inspect_response
from tutorial.items import Product
from tutorial.itemLoaders import ProductLoader


class PhoneTmallSpider(scrapy.Spider):
    name = 'phone_tmall'

    def start_requests(self):
        script = '''
        function main(splash, args)
            splash.images_enabled = false
            splash:go(args.url)
            splash:wait(args.wait)
            
            splash:init_cookies(splash:get_cookies())

            splash:select('.ui-page .ui-page-skip input.ui-page-skipTo'):setAttribute('value', args.pageNum)
            splash:select('.ui-page .ui-page-skip .ui-btn-s'):mouse_click()
            splash:wait(args.wait)

            return {
                html = splash:html(),
                cookies = splash:get_cookies()
            }
        end
        '''

        cookie = {
            "cna": "Rga8FhjPejYCAd0LIIdwBFyl",
            "t": "97626a1de2afe4c04f6623bb50adbbb2",
            "_tb_token_": "7333ee8bab93e",
            "cookie2": "1b4d89e10bcf1f7771297ae822b74e22",
            "_med": "dw:1280&dh:720&pw:1920&ph:1080&ist:0",
            "dnk": "%5Cu4E3A%5Cu4EC0%5Cu4E48%5Cu767B%5Cu5F55%5Cu540D%5Cu4E0D%5Cu80FD%5Cu6539",
            "lid": "%E4%B8%BA%E4%BB%80%E4%B9%88%E7%99%BB%E5%BD%95%E5%90%8D%E4%B8%8D%E8%83%BD%E6%94%B9",
            "enc": "F3H91y7mufXNuqbMh1iG26wqgo%2BdDUoz44eFtr6N412W5llLk5voXU4%2Fp4ZQ77usW90delDJUSqbJh9qy9lsqw%3D%3D",
            "_uab_collina": "158053798371889794334634",
            "res": "scroll%3A1263*5638-client%3A1263*526-offset%3A1263*5638-screen%3A1280*720",
            "pnm_cku822": "098%23E1hvgQvUvbpvUpCkvvvvvjiPn2sZ6j18n2LU0jnEPmPWljinR2FyAj1bnLspsjnhRuwCvvpvvUmmvphvC9vhvvCvpvyCvhQp0VGvCluQD7zhV8tYVVzh1jZ7%2B3%2BiaNoxfBeK4Qtr1WClHdBYLWFwAWQ7RAYVyO2vqbVQWl4vsRFE%2BFIlBqeviNoAdcZIGExrQ8gckphvC99vvOC0LTyCvv9vvUmzS6pNnfyCvm9vvvvvphvvvvvv99Cvpv9gvvmmvhCvmhWvvUUvphvUI9vv99Cvpvkk2QhvCPMMvvvtvpvhvvvvvv%3D%3D",
            "cq": "ccp%3D0",
            "l": "cBrCxFAeQ_Jr-j-2BOCNCuI-1u7tSIRAguPRwc8Mi_5Ka6LT6P_Oo4GiUFp6cjWdtLLB4082vew9-etksDILNztqTtrR.",
            "isg": "BOPj11iGuf-fB3XLHTduQfa4cieN2Hca6rhwlBVAN8K9VAJ2nareakGOTiTadM8S",
            "uc1": "cookie16",
            "uc3": "id2",
            "tracknick": "%5Cu4E3A%5Cu4EC0%5Cu4E48%5Cu767B%5Cu5F55%5Cu540D%5Cu4E0D%5Cu80FD%5Cu6539",
            "_l_g_": "Ug%3D%3D",
            "uc4": "nk4",
            "unb": "3223980991",
            "lgc": "%5Cu4E3A%5Cu4EC0%5Cu4E48%5Cu767B%5Cu5F55%5Cu540D%5Cu4E0D%5Cu80FD%5Cu6539",
            "cookie1": "Vq8xMrHup67eKsAwVq5tjlAujdZ%2F8d2S7heFCb%2BQbJk%3D",
            "login": "true",
            "cookie17": "UNJTLMPbwyW6AQ%3D%3D",
            "_nk_": "%5Cu4E3A%5Cu4EC0%5Cu4E48%5Cu767B%5Cu5F55%5Cu540D%5Cu4E0D%5Cu80FD%5Cu6539",
            "sg": "%E6%94%B91a",
            "csg": "147c2c64"
        }

        headers = {
            ':authority': 'list.tmall.com',
            'referer': 'https://www.tmall.com/',
            'upgrade-insecure-requests': 1,
            ':path': '/search_product.htm?q=%CA%D6%BB%FA&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton',
        }

        argsDict = {
            'url': r'https://list.tmall.com/search_product.htm?spm=a220m.1000858.1000724.9.3c3f2a687AClyu&s=60&q=%CA%D6%BB%FA&sort=s&style=g&from=mallfp..pc_1_searchbutton&type=pc',
            'wait': 5,
            'pageNum': 1,
            'lua_source': script,
        }

        # 使用的 virtualbox 虚拟机，性能有限，一次爬10页，手动搜索看到一共有100页
        for i in range(10):
            yield scrapy_splash.SplashRequest(
                argsDict['url'], self.parse, args=argsDict, endpoint='execute', priority=2,
                # cookies=cookie,
                # headers =headers,
                meta={
                    'pageNum': argsDict['pageNum']
                }
            )

            argsDict['pageNum'] += 1
            break

    def parse(self, response):
        inspect_response(response, self)
        urls = response.css('#J_ItemList .product .productImg-wrap a::attr(href)').getall()
        self.logger.info(len(urls))
        # pageNum = response.meta['pageNum']

        # script = '''
        # function main(splash, args)
        #     splash.images_enabled = false
        #     splash:go(args.url)
        #     splash:wait(5)

        #     return splash:html()
        # end
        # '''

        # argsDict = {
        #     'url': '',
        #     'lua_source': script,
        # }

        # for url in urls:
        #     if not url.startswith('https:'):
        #         url = 'https:' + url

        #     # argsDict['url'] = 'https://item.jd.com/7509313.html'  # 32页评论
        #     argsDict['url'] = url

        #     yield scrapy_splash.SplashRequest(
        #         url, self.parseProduct, args=argsDict, endpoint='execute', priority=1,
        #         meta={
        #             'pageNum': pageNum
        #         }
        #     )

    def parseProduct(self, response):
        urls = response.css('#spec-list li img::attr(src)').getall()
        productLoader = self.getLoader(response)

        pattern = r'commentVersion:\'\d*\','
        commentVersion = response.css('script::text').re_first(pattern)
        commentVersion = re.sub(r'\D', '', commentVersion)

        meta = {
            'l': productLoader,
            'imgs': [x for x in range(len(urls))],
            'referer': response.url,    # 评论接口要用
            'commentVersion': commentVersion,    # 评论接口要用
        }

        for url in urls:
            url = self.checkImgUrl(url)

            yield scrapy.Request(url=url, callback=self.parseImgs, meta=meta, dont_filter=True)

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
