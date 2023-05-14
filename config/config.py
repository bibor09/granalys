from yaml import loader, load
import os
import sys
import logging

class Config:
    def __init__(self, mode):
        dir = os.path.dirname(__file__)
        if mode == "web":
            rel_path = "granalys_web.yml"
        else:
            rel_path = "granalys_cmd.yml"
        self.abs_file_path = os.path.join(dir, rel_path)

        try:
            with open(self.abs_file_path) as f:
                data = load(f, Loader=loader.SafeLoader)

            self.neo4j_auth = data['neo4j.user'], data['neo4j.passwd']
            self.neo4j_uri = data['neo4j.uri']
            self.neo4j_db = data['neo4j.db']

            if mode == "web":
                self.github_auth_token = data['github.auth.token']
                self.granalys_web_url = data['granalys.web.url']
                self.mongo_db = data['mongodb.db']
                self.mongo_url = data['mongodb.url']
                self.mongo_port = data['mongodb.port']
        except:
            logging.error(f"Invalid configuration file {self.abs_file_path}")
            sys.exit()        