from pymongo import MongoClient, errors, DESCENDING
from pydantic import BaseModel

class Database:
    def __init__(self, host, port, name, username, password, collection):
        self.name = name
        self.client = MongoClient(host, port, username=username, password=password)
        self.db = self.client[name]
        self.collection = self.db[collection]

    def close(self):
        self.client.close()
    
    ''' CRUD operations '''

    def save(self, entity: BaseModel):
        return self.collection.insert_one(entity.dict())
    
    def find_one(self, attributes: dict):
        return self.collection.find_one(attributes)
    
    def get_gd_id(self, attributes: dict):
        result = self.collection.find_one(attributes)
        return result["gd_id"]
    
    def get_files_w_stats_from_date(self, date, entity: BaseModel):
        file_stats = dict()
        for file in entity["statistics_all"].keys():
            file_stats[file] = self.get_all_statistics_for_file(entity["user"], entity["repo"], entity["branch"], date, file)      
        return file_stats

    def get_all_statistics_for_file(self, user, repo, branch, curr_date, file):
        result = self.collection.find({
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

    # Returns a list of branches with their latest pushes for the given user and repo
    def get_all_branches_with_latest_push(self, user, repo):
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
        result = self.collection.aggregate(pipeline)
        result = [{"branch":r["_id"], "gd_id": self.get_gd_id({"user":user, "repo":repo, "branch":r["_id"], "created":r["created"]})} for r in result]
        result.sort(key=lambda x: x["branch"])
        return result
    