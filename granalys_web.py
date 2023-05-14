import argparse
import sys
import os
import subprocess

# parser = argparse.ArgumentParser(description='Granalys')
# args = parser.parse_args()

# def main(args):
#     logging.getLogger().setLevel(logging.INFO)

#     [file] = args.file
#     if not os.path.isfile(file):
#         logging.error(f"Invalid or non-existent file")
#         sys.exit()

#     conf = Config("web")
#     instance = Granalys(conf.get_neo4j_uri(), conf.get_neo4j_auth(), conf.get_neo4j_db())
#     instance.start_cmd(file)
#     instance.close()

# if __name__ == "__main__":
#     subprocess.run("waitress-serve --port --url-scheme=https ")
#     subprocess.run("flask --app web/app.py run --host 0.0.0.0")