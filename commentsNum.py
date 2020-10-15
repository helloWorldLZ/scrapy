import pymongo
import re
import json

client = pymongo.MongoClient("localhost", 27017)
collection = client.jd.phone
documents = collection.find({
	'comments': {'$exists': True}
})

dic = {}
for document in documents:
	pageNum = document['pageNum']

	if pageNum not in dic.keys():
		dic[pageNum] = 0

	num = len(document['comments'])
	dic[pageNum] += num

fileName = 'tmp.json'
with open(fileName, 'w', encoding='utf-8') as f_obj:
    urls = json.dump(dic, f_obj, indent=4)