from yaml import loader, load
import os

dir = os.path.dirname(__file__)
rel_path = "granalys.yml"
abs_file_path = os.path.join(dir, rel_path)

def get_config():
    with open(abs_file_path) as f:
        data = load(f, Loader=loader.SafeLoader)
    return data
