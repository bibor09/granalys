from yaml import loader, load
import os

dir = os.path.dirname(__file__)
rel_path = "granalys_cmd.yml"
abs_file_path = os.path.join(dir, rel_path)

def get_uri():
    with open(abs_file_path) as f:
        data = load(f, Loader=loader.SafeLoader)
    return data['neo4j.uri']

def get_db():
    with open(abs_file_path) as f:
        data = load(f, Loader=loader.SafeLoader)
    return data['neo4j.db']

def get_auth():
    with open(abs_file_path) as f:
        data = load(f, Loader=loader.SafeLoader)
    return data['neo4j.user'], data['neo4j.passwd']
