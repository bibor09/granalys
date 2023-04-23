from pymongo import MongoClient, errors, DESCENDING
from pydantic import BaseModel

class Database:
    def __init__(self, host, port, name):
        self.name = name
        self.client = MongoClient(host, port)
        self.db = self.client[name]

    def get_coll(self, coll_name):
        return self.db[coll_name]
    
    def save(self, coll_name, entity: BaseModel):
        collection = self.get_coll(coll_name)
        print("Saved", entity)
        return collection.insert_one(entity.dict())

    def get(self, coll_name, attributes: dict):
        collection = self.get_coll(coll_name)
        return collection.find(attributes)
    
    def get_one(self, coll_name, attributes: dict):
        collection = self.get_coll(coll_name)
        return collection.find_one(attributes)
    
    def get_distinct(self, coll_name, filter: str, attributes: dict):
        collection = self.get_coll(coll_name)
        return collection.distinct(filter, attributes)
    
    def get_newest_analysis(self, coll_name, attributes):
        collection = self.get_coll(coll_name)
        return collection.find(attributes).sort({'created': 1}).limit(1)
    
    def get_gd_id(self, coll_name, attributes):
        collection = self.get_coll(coll_name)
        result = collection.find_one(attributes)
        return result["gd_id"]
    
    def get_all(self, coll_name, user, repo):
        collection = self.get_coll(coll_name)
        pipeline = [
            {
                "$match": {
                    "user": user,
                    "repo": repo,
                }
            }, 
            {
                "$sort": {
                    "created": DESCENDING
                }
            },
            {
                "$group": {
                    "_id": "$branch",
                    "created": {"$first": "$created"},
                },
            },
        ]
        result = collection.aggregate(pipeline)
        result = [{"branch":r["_id"], "gd_id": self.get_gd_id("analysis", {"user":user, "repo":repo, "branch":r["_id"], "created":r["created"]})} for r in result]
        result.sort(key=lambda x: x["branch"])
        print(result)
        return result