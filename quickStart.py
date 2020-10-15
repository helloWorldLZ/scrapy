from scrapy.cmdline import execute
# import sys
# import os

# 命令行执行需要将当前目录加入到pythonpath中，pycharm不需要这段代码
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(['scrapy', 'crawl', 'camera'])
# execute(['scrapy', 'crawl', 'example'])
