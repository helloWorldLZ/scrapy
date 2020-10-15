import pymongo

client = pymongo.MongoClient("localhost", 27017)
collection = client.jd.imgTest2

documents = collection.find({})

document = documents[0]
imgs = document['imgs']

for img in imgs:
	b = img['b']
	filename = img['path']

	with open(filename, 'wb') as f:
            f.write(b)


