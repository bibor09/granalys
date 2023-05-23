from db.database import Database
from pydantic import BaseModel

class Business:
    def __init__(self, db: Database):
        self.db = db

    def get_all_branches(self, coll_name, user, repo):
        return self.db.get_distinct(coll_name, 'branch', {'user':user, 'repo':repo})
    
    def get(self, coll_name, attributes: dict):
        return self.db.get(coll_name, attributes)
    
    def get_one(self, coll_name, attributes: dict):
        return self.db.get_one(coll_name, attributes)
        
    def get_newest_analysis(self, coll_name, attributes):
        return self.db.get_newest_analysis(coll_name, attributes)
    
    def save(self, coll_name, entity: BaseModel):
        return self.db.save(coll_name, entity)
    
    def get_file_statistics_from_date(self, coll_name, date, entity: BaseModel):
        file_stats = dict()
        for file in entity["statistics_all"].keys():
            file_stats[file] = self.db.get_all_statistics_for_file(coll_name, entity["user"], entity["repo"], entity["branch"], date, file)      
        return file_stats

