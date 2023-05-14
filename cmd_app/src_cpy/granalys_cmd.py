import argparse
import sys
import os
import logging
from config import get_auth, get_db, get_uri
from analyzer import Granalys

parser = argparse.ArgumentParser(description='Granalys')
parser.add_argument('file', nargs=1, help='Filename')
args = parser.parse_args()

def main(args):
    logging.getLogger().setLevel(logging.INFO)

    [file] = args.file
    if not os.path.isfile(file):
        logging.error(f"Invalid or non-existent file")
        sys.exit()

    instance = Granalys(get_uri(), get_auth(), get_db(), True)
    instance.loop(file)
    instance.close()

if __name__ == "__main__":
    main(args)