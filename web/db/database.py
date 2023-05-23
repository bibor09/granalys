from pymongo import MongoClient, errors, DESCENDING
from pydantic import BaseModel

class Database:
    def __init__(self, host, port, name, username, password):
        self.name = name
        self.client = MongoClient(host, port, username=username, password=password)
        self.db = self.client[name]

    def close(self):
        self.client.close()

    def get_coll(self, coll_name):
        return self.db[coll_name]
    
    def save(self, coll_name, entity: BaseModel):
        collection = self.get_coll(coll_name)
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
    
    def get_all_statistics_for_file(self, coll_name, user, repo, branch, curr_date, file):
        collection = self.get_coll(coll_name)
        result = collection.find({
            "user": user,
            "repo": repo,
            "branch": branch,
            "created": {"$lte": curr_date}
        })
        statistics = {"comment": [], "complexity": [], "inst": [], "loc": [], "created": []}
        
        for entity in result:
            try:
                file_stat = entity["statistics_all"][file]
            except:
                continue

            comment_ratio = float(file_stat["comment"])
            loc = int(file_stat["loc"])
            complexity = int(file_stat["complexity"])
            if type(file_stat["inst"]) == str:
                inst = 0.0
            else:
                inst = float(file_stat["inst"])

            statistics["comment"].append(comment_ratio*loc)
            statistics["loc"].append(loc)
            statistics["complexity"].append(complexity)
            statistics["inst"].append(inst)
            statistics["created"].append(entity["created"].strftime("%Y-%m-%d %H:%M:%S"))

        return statistics


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
        return result
    