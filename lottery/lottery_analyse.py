import pymongo
import json
import random
import itertools


# 第六条  双色球投注区分为红色球号码区和蓝色球号码区，红色球号码区由1-33共三十三个号码组成，蓝色球号码区由1-16共十六个号码组成。
# 投注时选择6个红色球号码和1个蓝色球号码组成一注进行单式投注，每注金额人民币2元。
# 红色球的6个数不可以重复，蓝色的1个号码可以跟红色球的6个数里的一个一样

client = pymongo.MongoClient("localhost", 27017)
collection = client.lottery.ssq


# 插入新的记录
def insert_records():
	client.lottery.ssq.insert_one({
		'red_balls': ['03', '06', '08', '11', '19', '28'],	
		'blue_balls': '08',
		'issue': '2020051',
		'date': '2020-06-16',
	})


#	获取红色号码历史记录
def get_histories():
	documents = collection.find({})
	histories = [document['red_balls'] for document in documents]

	return histories


#	分析蓝号跨度变化
def distance_statistic():
	documents = collection.find({})
	dic = {}
	histories = {}		#	{isssue: blue_ball} 的形式

	for document in documents:
		issue = document['issue']

		issue_key = issue[:4]
		if issue_key not in dic.keys():
			dic[issue_key] = []

		dic[issue_key] += [int(issue)]

		histories[issue] = document['blue_balls']

	#	排序
	res = {}
	for issue_k, v in dic.items():
		max_issue = max(v)
		min_issue = min(v)

		if issue_k not in res.keys():
			res[issue_k] = []

		for i in range(160):
			 key_i = str(max_issue)
			 blue_ball = histories[key_i]

			 res[issue_k] += [blue_ball]

			 max_issue -= 1
			 if max_issue < min_issue:
			 	break

	fileName = './statistics/blue_balls_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(res, f_obj, indent=4)

	distances = {}
	for blue_balls in res.values():
		
		for j in range(len(blue_balls)-1):
			max_ball = max([int(blue_balls[j]), int(blue_balls[j+1])])
			min_ball = min([int(blue_balls[j]), int(blue_balls[j+1])])

			distance = max_ball - min_ball
			distance_key = str(distance)

			if distance_key not in distances.keys():
				distances[distance_key] = 0

			distances[distance_key] += 1

	fileName = './statistics/distance_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(distances, f_obj, indent=4)


#	统计每个号码出现的总次数
def times_statistic():
	documents = collection.find({})

	red_dic = {}
	blue_dic = {}

	for document in documents:
		red_balls = document['red_balls']
		blue_balls = document['blue_balls']

		if blue_balls not in blue_dic.keys():
			blue_dic[blue_balls] = 0

		blue_dic[blue_balls] += 1

		for red_ball in red_balls:
			if red_ball not in red_dic.keys():
				red_dic[red_ball] = 0

			red_dic[red_ball] += 1

	dic = {
		'red_dic': red_dic,
		'blue_dic': blue_dic
	}

	fileName = './statistics/times_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)


#	奇偶个数统计
def odd_even_statistic():
	histories = get_histories()
	odd_dic = {}
	even_dic = {}

	for history in histories:
		res = [red_number for red_number in history if (int(red_number) % 2) > 0]
		times = len(res)		#	奇数个数

		dic_key = str(times)
		if dic_key not in odd_dic.keys():
			odd_dic[dic_key] = 0

		odd_dic[dic_key] += 1

		dic_key = str(6 - times)
		if dic_key not in even_dic.keys():
			even_dic[dic_key] = 0

		even_dic[dic_key] += 1

	dic = {
		'odd': odd_dic,
		'even': even_dic
	}

	fileName = './statistics/odd_even_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)


#	最小号码统计
def min_start_statistic():
	histories = get_histories()

	min_start = {}
	for history in histories:
		red_numbers = [int(red_ball) for red_ball in history]
		start = min(red_numbers)
		key = str(start)

		if key not in min_start.keys():
			min_start[key] = 0

		min_start[key] += 1

	fileName = './statistics/min_start_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(min_start, f_obj, indent=4)


#	统计各组号码间发生重号时，重号的分布情况
def cross_similarity_statistic():
	histories = get_histories()
	length = len(histories)
	dic = {}

	for i in range(length):
		red_balls_1 = histories[i]
		histories_copy = histories[(i+1):]

		# same_records = []
		for red_balls_2 in histories_copy:

			res = [red_1 for red_1 in red_balls_1 if red_1 in red_balls_2]
			similarity = len(res)
			key = str(similarity)

			# if similarity == 6:
			# 	same_records.append(red_balls_2)

			if key not in dic.keys():
				dic[key] = 0

			dic[key] += 1

		# if len(same_records) > 0:
		# 	print(same_records)

	fileName = './statistics/cross_similarity_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)


#	统计每组号码与其它号码的最大相似度，感觉没啥用
def max_similarity_statistic():
	histories = get_histories()
	length = len(histories)
	dic = {}

	for i in range(length):
		red_balls_1 = histories[i]
		histories_copy = histories[:]
		histories_copy.pop(i)

		max_similarity = 0
		for red_balls_2 in histories_copy:

			res = [red_1 for red_1 in red_balls_1 if red_1 in red_balls_2]
			similarity = len(res)

			if similarity > max_similarity:
				max_similarity = similarity

		max_key = str(max_similarity)
		if max_key not in dic.keys():
			dic[max_key] = 0

		dic[max_key] += 1

	fileName = './statistics/max_similarity_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)


#	红号组合出现的范围统计，感觉没啥用
def combinations_range():
	histories = get_histories()
	combinations = itertools.combinations([i+1 for i in range(33)], 6)
	# print(len(list(combinations)))		#	110,7568 种组合

	arr = []
	i = 0
	for combination in combinations:
		red_numbers = list(combination)
		i += 1

		is_exclusive2 = is_exclusive(red_numbers)
		if is_exclusive2:
			continue

		red_sum = sum(red_numbers)
		if (red_sum < 41) or (red_sum > 170):
			continue

		red_balls = format_conversion(red_numbers)

		for j in range(len(histories)):

			if red_balls == histories[j]:
				arr.append(i)
				histories.pop(j)
				break

	print(len(arr))

	dic = {
		'max': max(arr),
		'min': min(arr),
		'res': arr,
	}

	fileName = './statistics/combinations_range_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)


#	红号和数统计
def red_sum_statistic():
	documents = collection.find({})
	res = []

	for document in documents:
		red_balls_1 = document['red_balls']

		red_balls_2 = [int(red_1) for red_1 in red_balls_1]

		res.append(sum(red_balls_2))

	dic = {
		'min': min(res),
		'max': max(res),
		'res': res
	}

	fileName = './statistics/red_sum_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)


#	判断相似度分布情况
def test_similarity(red_numbers, mode=0):
	red_balls = red_numbers

	if mode == 1:
		red_balls = format_conversion(red_numbers)

	histories = get_histories()

	dic = {}
	for history in histories:
		res = [red_ball for red_ball in red_balls if red_ball in history]
		similarity = len(res)
		key = str(similarity)

		if key not in dic.keys():
			dic[key] = 0

		dic[key] += 1

	print(dic)


#	转换为字符串格式
def format_conversion(red_numbers):
	red_balls = []

	for red_number in red_numbers:
		red_ball = ''
		
		if red_number < 10:
			red_ball = '0' + str(red_number)
		else:
			red_ball = str(red_number)

		red_balls.append(red_ball)

	return red_balls


#	排除连号高的组合
def get_exclusions():
	exclusions = []

	for i in range(31):
		start = i + 1
		exclusions.append([start, start+1, start+2])

	return exclusions


#	判断是否含有需要排除掉的固定组合
def is_exclusive(red_numbers):
	is_exclusive = False
	exclusions = get_exclusions()

	#	排除固定组合
	for combination in exclusions:
		res = [red_number for red_number in combination if red_number in red_numbers]

		if len(res) == len(combination):
			is_exclusive = True
			break

	#	奇偶性排除
	if not is_exclusive:
		res = [red_number for red_number in red_numbers if (red_number % 2) > 0]
		times = len(res)		#	奇数个数

		if (times < 2) or (times > 4):
			is_exclusive = True

	# print(is_exclusive)

	return is_exclusive


#	生成最大相似度为 n 的号码
def combinations_max_similarity_3(low_value, high_value):
	histories = get_histories()
	combinations = itertools.combinations([i+1 for i in range(33)], 6)
	# print(len(list(combinations)))		#	110,7568 种组合

	arr = []
	for combination in combinations:
		red_numbers = list(combination)

		is_exclusive2 = is_exclusive(red_numbers)
		if is_exclusive2:
			continue

		# red_sum = sum(red_numbers)
		# if (red_sum < low_value) or (red_sum > high_value):
		# 	continue

		red_balls = format_conversion(red_numbers)

		max_similarity = 0
		for history in histories:
			if red_balls == history:
				max_similarity = 6
				break

			res = [red_ball for red_ball in red_balls if red_ball in history]
			similarity = len(res)
			
			if similarity > max_similarity:
				max_similarity = similarity

			if similarity > 3:
				break

		if max_similarity < 4:
			arr.append(red_balls)

	print(len(arr))

	fileName = './statistics/combinations_max_similarity_3.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(arr, f_obj)


#	出号
def combinations():
	histories = get_histories()
	combinations = itertools.combinations([i+1 for i in range(33)], 6)
	# print(len(list(combinations)))		#	110,7568 种组合

	dic = {}
	i = 0
	for combination in combinations:
		red_numbers = list(combination)
		i += 1

		if i < 864854:
			continue

		is_exclusive2 = is_exclusive(red_numbers)
		if is_exclusive2:
			continue

		red_sum = sum(red_numbers)
		if (red_sum < 70) or (red_sum > 130):
			continue

		red_balls = format_conversion(red_numbers)

		key_i = str(i)
		if key_i not in dic.keys():
			dic[key_i] = {'balls': red_balls}

		max_similarity = 0
		for history in histories:
			if red_balls == history:
				max_similarity = 6
				break

			res = [red_ball for red_ball in red_balls if red_ball in history]
			similarity = len(res)

			if similarity > max_similarity:
				max_similarity = similarity

			if similarity > 4:
				break

			dic2 = dic[key_i]

			key2 = str(similarity)
			if key2 not in dic2.keys():
				dic2[key2] = 0
			
			dic2[key2] += 1

		if max_similarity > 4:
			del dic[key_i]

		if len(dic.keys()) > 100000:
			break

	print(len(dic.keys()))

	fileName = './statistics/combinations_50W_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)


# 获取连续 n 个号码的历史记录
def is_serial(arr_n, history):
	is_serial = False

	for arr in arr_n:
		res = [red_ball for red_ball in arr if red_ball in history]

		if len(res) == len(arr):
			is_serial = True
			break

	return is_serial


#	判断不同长度连号的分布情况
def serials_statistic():
	arr2 = [format_conversion([i+1, i+2]) for i in range(32)]
	arr3 = [format_conversion([i+1, i+2, i+3]) for i in range(31)]
	arr4 = [format_conversion([i+1, i+2, i+3, i+4]) for i in range(30)]
	arr5 = [format_conversion([i+1, i+2, i+3, i+4, i+5]) for i in range(29)]
	arr6 = [format_conversion([i+1, i+2, i+3, i+4, i+5, i+6]) for i in range(28)]

	histories = get_histories()

	serials_6 = [history for history in histories if is_serial(arr6, history)]
	serials_5 = [history for history in histories if is_serial(arr5, history) and not is_serial(arr6, history)]
	serials_4 = [history for history in histories if is_serial(arr4, history) and not is_serial(arr5, history)]
	serials_3 = [history for history in histories if is_serial(arr3, history) and not is_serial(arr4, history)]
	serials_2 = [history for history in histories if is_serial(arr2, history) and not is_serial(arr3, history)]
	serials_0 = [history for history in histories if not is_serial(arr2, history)]

	dic = {
		'serials_6': len(serials_6),
		'serials_5': len(serials_5),
		'serials_4': len(serials_4),
		'serials_3': len(serials_3),
		'serials_2': len(serials_2),
		'serials_0': len(serials_0),
		'keys_2': {},
	}
	dic2 = dic['keys_2']
	
	for history in serials_2:
		for arr in arr2:
			key2 = '_'.join(arr)

			if key2 not in dic2.keys():
				dic2[key2] = 0

			res = [red_ball for red_ball in arr if red_ball in history]

			if len(res) == 2:
				dic2[key2] += 1

	fileName = './statistics/serials_statistic.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(dic, f_obj, indent=4)
		

# ================================================================
# 52(周) * 3(期) = 156(期) * 2(元) = 312(元)

# times_statistic()		#	统计每个号码出现的总次数

# cross_similarity_statistic()		#	统计各组号码间发生重号时，出现的重号个数

# max_similarity_statistic()		#	统计每组号码与其它号码的最大相似度，感觉没啥用

# combinations_range()		#	红号组合范围统计

# red_sum_statistic()		#	红号和数统计

# is_exclusive([1,20,18,16,10,12])

# combinations_max_similarity_3(70, 130)		#	生成相似度为 n 的号码
# combinations_max_similarity_3(41, 170)		#	生成相似度为 n 的号码

# combinations()		#	出号

# serials_statistic()		#	判断不同长度连号的分布情况

test_similarity([1, 9, 7, 12, 25, 28], 1)		#	判断相似度分布
# test_similarity(['04', '09', '19', '20', '21', '26'])		#	判断相似度分布

# insert_records()

# distance_statistic()

# odd_even_statistic()

# min_start_statistic()

# max_similarity < 4，没有和数限制
# arr2 = [["02", "10", "14", "26", "31", "33"], ["09", "16", "19", "29", "30", "33"], ["09", "13", "17", "23", "29", "33"]]

def ssq():
	arr2 = [

		["02", "10", "14", "26", "31", "33"],		#	9====

		["09", "16", "19", "29", "30", "33"],		#	10=====

		["09", "13", "17", "23", "29", "33"],		#	5==============
				
		["01", "02", "15", "18", "21", "26"],		#	11=========

		["03", "08", "11", "20", "25", "30"],		#	14===========

				
		["04", "09", "19", "21", "27", "30"],		#	12==========

		["05", "10", "18", "20", "27", "32"],		#	15=============

		["06", "18", "19", "25", "29", "30"],		#	3=============

		["07", "08", "23", "25", "26", "29"],		#	16===========

		["08", "12", "15", "20", "21", "26"],		#	13===========

				
		["04", "09", "17", "18", "25", "28"],		#	6=========

		["01", "04", "09", "10", "22", "24"],		#	7==========
	]

	dic = {}
	for arr in arr2:
		test_similarity(arr)
		print()
		print('============================================================================')

		for key_i in arr:

			if key_i not in dic.keys():
				dic[key_i] = 0

			dic[key_i] += 1

	dic_keys = list(dic.keys())
	dic_keys.sort()

	ssq = {
		'dic_keys': dic_keys,
		'dic_keys_length': len(dic_keys),
		'res': dic,
	}
	fileName = './statistics/ssq.json'
	with open(fileName, 'w', encoding='utf-8') as f_obj:
		urls = json.dump(ssq, f_obj, indent=4)


# ssq()