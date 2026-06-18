from pymongo import MongoClient
# from bson.objectid import ObjectId

class PharmEasyDB:
    database = "scrapy"
    collection_name = "pharmeasy"

    def __init__(self, host="localhost", port=27017):
        self.client = MongoClient(host, port)
        self.db = self.client[self.database]
        self.model = self.db[self.collection_name]

    def insert_data(self, record):
        result = self.model.insert_one(record)
        print(result.inserted_id)

    def get(self, id):
        doc = self.model.find_one({"_id": id})
        return doc
    
    def getAll(self):
        doc = self.model.find({})
        return doc
    
    def deleteMany(self):
        result = self.model.delete_many({})
        print(f"Deleted {result.deleted_count} documents")


pharmeasydb = PharmEasyDB()

# pharmeasy_db.deleteMany()

