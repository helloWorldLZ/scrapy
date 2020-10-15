import time
import pyecharts
import pyecharts.options as opts

from pyecharts.charts import Line

# 评论数
comments_count = [
	None,
	57050,
	48934,
	38426,
	28485,
	27473,
	27350,
	22886,
	28406,
	18949,
	18474,
]

#  请求数
request_count = [
	None,
	6303,
	5484,
	4585,
	3426,
	3731,
	3404,
	2804,
	3427,
	2438,
	2462,
]

start_time = [
	'2020-01-19 11:03:32',
	'2020-01-19 21:44:28',
	'2020-01-20 08:49:03',
	'2020-01-20 20:26:19',
	'2020-01-21 08:19:50',
	'2020-01-21 19:25:30',
	'2020-01-22 09:43:43',
	'2020-01-22 16:27:43',
	'2020-01-23 11:12:12',
	'2020-01-23 20:17:27',
	'2020-02-04 14:54:13',		# dangdang
]

end_time = [
	'2020-01-19 21:09:44',
	'2020-01-20 06:21:54',
	'2020-01-20 15:59:25',
	'2020-01-21 01:34:11',
	'2020-01-21 13:55:38',
	'2020-01-22 00:29:15',
	'2020-01-22 14:03:52',
	'2020-01-22 21:37:43',
	'2020-01-23 14:34:44',
	'2020-01-23 23:58:36',
	'2020-02-04 16:47:29',		# dangdang
]

data = [None]
for i in range(11):
	start = time.mktime(time.strptime(start_time[i], '%Y-%m-%d %H:%M:%S'))
	end = time.mktime(time.strptime(end_time[i], '%Y-%m-%d %H:%M:%S'))

	res = (end - start) / 3600
	data.append('{:.1f}'.format(res))

xlables = [i for i in range(13)]	
xlables[11] = '当当网'

c = (
    Line()
    .add_xaxis(xlables)
    .add_yaxis("评论数", comments_count, symbol_size=10)
    .add_yaxis("请求数", request_count, symbol='triangle', symbol_size=10,
		linestyle_opts=opts.LineStyleOpts(
			type_='dotted'
		))
    .extend_axis(yaxis=opts.AxisOpts(
    	name='总耗时\n\r(单位:小时)',
		name_textstyle_opts=opts.TextStyleOpts(
			font_size=16,
			# padding=[None, None, None, 50]
		),
    ))
    .set_global_opts(
    	xaxis_opts=opts.AxisOpts(
    		name='页码',
    		name_location='start',
    		name_textstyle_opts=opts.TextStyleOpts(
    			font_size=16,
    			padding=[60, -35, None, None]
    			# padding=[60, None, None, -50]
    		),
    		boundary_gap=False,
    		axistick_opts=opts.AxisTickOpts(
				is_inside=True
    		)
    	),
    	yaxis_opts=opts.AxisOpts(
    		name='(单位:个)',
    		name_textstyle_opts=opts.TextStyleOpts(
    			font_size=16,
    			padding=[None, None, 5, -50]
    		),
    		axistick_opts=opts.AxisTickOpts(
				is_inside=True
    		)
    	)
    )
    # .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
)

line = (
	Line()
	.add_xaxis(xlables)
	.add_yaxis(
		"总耗时", data[:-1], yaxis_index=1, symbol='roundRect', symbol_size=10,
		label_opts=opts.LabelOpts(
			position='bottom'
		),
		linestyle_opts=opts.LineStyleOpts(
			type_='dashed'
		),
    	markpoint_opts=opts.MarkPointOpts(
    		data=[opts.MarkPointItem(
    			name='当当网 1-5 页',
    			coord=['当当网', data[-1]],
    			symbol_size=20,
    			value=data[-1],
			)],
			label_opts=opts.LabelOpts(
				position='top',
			),
		)
	)
)

c.overlap(line)
c.render('line.html')
