import argparse
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/config")
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/analyzer")
from config.config import Config
from analyzer.analyzer import Granalys


parser = argparse.ArgumentParser(description='Granalys')
parser.add_argument('file', nargs=1, help='Filename')
args = parser.parse_args()

def main(args):
    logging.getLogger().setLevel(logging.INFO)

    [file] = args.file
    if not os.path.isfile(file):
        logging.error(f"Invalid or non-existent file")
        sys.exit()

    conf = Config("cmd")
    instance = Granalys(conf.neo4j_uri, conf.neo4j_auth, conf.neo4j_db, True)
    instance.start_cmd(file)
    instance.close()

if __name__ == "__main__":
    main(args)