import pymongo
import re
import json

fileName = 'logs/urls40.json'
with open(fileName, encoding='utf-8') as f_obj:
    urls = json.load(f_obj)

url_set = {re.sub(r'\D', '', url) for url in urls}

client = pymongo.MongoClient("localhost", 27017)
collection = client.jd.camera
documents = collection.find({
	'pageNum': 40
})

id_set = {document['productId'] for document in documents}
result_set = url_set - id_set

lostUrl = 'https://item.jd.com/{}.html'
lostUrls = [lostUrl.format(res) for res in result_set]
fileName = 'lostUrls.json'
with open(fileName, 'a', encoding='utf-8') as f_obj:
    urls = json.dump(lostUrls, f_obj, indent=4)
