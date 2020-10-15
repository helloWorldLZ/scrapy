import json

import pyecharts
import pyecharts.options as opts

from pyecharts.charts import Scatter
from pyecharts.charts import Bar

#	lottery_results_visualization

#	号码次数柱状图
def times_statistic(file_name):
	dic = {}
	fileName = './statistics/' + file_name +'.json'
	with open(fileName, encoding='utf-8') as f_obj:
	    dic = json.load(f_obj)

	red_dic = dic['blue_dic']

	c = Bar()
	c.add_xaxis(list(red_dic.keys()))
	c.add_yaxis('', list(red_dic.values()))

	return c.render('./visualization/' + file_name +'.html')


#	最小开始数字数柱状图
def min_start_statistic(file_name):
	dic = {}
	fileName = './statistics/' + file_name +'.json'
	with open(fileName, encoding='utf-8') as f_obj:
	    dic = json.load(f_obj)

	c = Bar()
	c.add_xaxis(list(dic.keys()))
	c.add_yaxis('', list(dic.values()))

	return c.render('./visualization/' + file_name +'.html')


#	奇偶个数柱状图
def odd_even_statistic(file_name):
	dic = {}
	fileName = './statistics/' + file_name +'.json'
	with open(fileName, encoding='utf-8') as f_obj:
	    dic = json.load(f_obj)

	even_dic = dic['even']
	odd_dic = dic['odd']

	c = Bar()
	c.add_xaxis([i for i in range(7)])
	c.add_yaxis('偶数个数', [even_dic[str(i)] for i in range(7)])
	c.add_yaxis('奇数个数', [odd_dic[str(i)] for i in range(7)])

	return c.render('./visualization/' + file_name +'.html')


#	蓝号跨度柱状图
def distance_statistic(file_name):
	dic = {}
	fileName = './statistics/' + file_name +'.json'
	with open(fileName, encoding='utf-8') as f_obj:
	    dic = json.load(f_obj)

	c = Bar()
	c.add_xaxis([i for i in range(16)])
	c.add_yaxis('', [dic[str(i)] for i in range(16)])

	return c.render('./visualization/' + file_name +'.html')


#	连号组合柱状图
def serials_statistic(file_name):
	dic = {}
	fileName = './statistics/' + file_name +'.json'
	with open(fileName, encoding='utf-8') as f_obj:
	    dic = json.load(f_obj)

	res = dic['keys_2']

	c = Bar()
	c.add_xaxis(list(res.keys()))
	c.add_yaxis('', list(res.values()))
	
	return c.render('./visualization/' + file_name +'.html')


#	和数散点图
def red_sum_statistic(file_name):
	dic = {}
	fileName = './statistics/' + file_name +'.json'
	with open(fileName, encoding='utf-8') as f_obj:
	    dic = json.load(f_obj)

	res = dic['res']

	c = Scatter()
	c.add_xaxis(xaxis_data=[i for i in range(len(res))])
	c.add_yaxis('', y_axis=res)
	
	return c.render('./visualization/' + file_name +'.html')


#	组合范围散点图
def combinations_range_statistic(file_name):
	dic = {}
	fileName = './statistics/' + file_name +'.json'
	with open(fileName, encoding='utf-8') as f_obj:
	    dic = json.load(f_obj)

	res = dic['res']

	c = Scatter()
	c.add_xaxis(xaxis_data=[i for i in range(len(res))])
	c.add_yaxis('', y_axis=res)
	
	return c.render('./visualization/' + file_name + '.html')


# (times_statistic('times_statistic'))
# (red_sum_statistic('red_sum_statistic'))
# (combinations_range_statistic('combinations_range_statistic'))
# (serials_statistic('serials_statistic'))
# (distance_statistic('distance_statistic'))
# (odd_even_statistic('odd_even_statistic'))
(min_start_statistic('min_start_statistic'))
