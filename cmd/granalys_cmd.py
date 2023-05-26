import argparse
import sys
import os
import logging

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current)+"/config")
sys.path.append(os.path.dirname(current)+"/analyzer")
from config import Config
from analyzer import Granalys


parser = argparse.ArgumentParser(description='Granalys')
args = parser.parse_args()

def main(args):
    logging.getLogger().setLevel(logging.INFO)
    conf = Config("cmd", "granalys_cmd.yml")
    instance = Granalys(conf.neo4j_uri, conf.neo4j_auth, conf.neo4j_db, True)
    instance.start_cmd()
    instance.close()

if __name__ == "__main__":
    main(args)