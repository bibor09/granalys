from flask import Flask, request, render_template, Response
from http import HTTPStatus
import requests
import os
import sys
import stat
import shutil
import logging
import re
import hashlib
import hmac
from decouple import config
from datetime import datetime
from git import Repo
from db.database import Database
from db.models import Analysis

current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current)+"/config")
sys.path.append(os.path.dirname(current)+"/analyzer")
from config import Config
from analyzer import Granalys


conf = Config("web", "granalys_web.yml")
# Initialize
app = Flask(__name__, static_url_path='', template_folder="templates", static_folder="static")
db = Database(conf.mongo_url, conf.mongo_port, name=conf.mongo_db, username=conf.mongo_user, password=conf.mongo_passwd, collection=conf.mongo_collection)
# bs = Business(db)

GITHUB_TOKEN = conf.github_auth_token
URL = conf.granalys_web_url

'''
    Web template displaying push event statistics.
'''
@app.route('/<user>/<repo>/<branch>/<gd_id>', methods=['GET'])
def event_by_id(user, repo, branch, gd_id):
    url_base = f"{user}/{repo}"
    all_analyses = db.get_all_branches_with_latest_push(user, repo)   #every branch
    curr_analysis = db.find_one({'user':user, 'repo':repo, 'branch': branch, 'gd_id': gd_id}) #current branch, actual analysis

    curr_analysis_date = curr_analysis['created']
    file_stats_chart = db.get_file_statistics_from_date(curr_analysis_date, curr_analysis)

    return render_template("index.html", all_analyses=all_analyses, curr_analysis=curr_analysis, url_base=url_base, file_stats_chart=file_stats_chart)


'''
    Listens for push events on configured Github repository. Analyzes modified files, and sets event status.
'''
@app.route('/', methods=['POST'])
def webhook():
    payload = request.json
    gd_id = request.headers.get('X-GitHub-Delivery')

    if not gd_id:
        logging.error("Github push event has invalid header format.")
        return Response("Error: Github push event has invalid header format.", status = HTTPStatus.BAD_REQUEST)       
        
    # Get payload information
    if 'ref' not in payload or 'repository' not in payload or 'full_name' not in payload['repository'] or 'clone_url' not in payload['repository'] or 'commits' not in payload:
        logging.error("Github push event has invalid payload format.")
        return Response("Error: Github push event has invalid payload format.", status = HTTPStatus.BAD_REQUEST)
    
    # Verify signature
    ver_resp = verify_signature(request.data, config("SECRET_TOKEN"), request.headers.get("X-Hub-Signature-256"))
    if ver_resp:
        return ver_resp
    
    branch = payload['ref'].split('/')[-1]
    repo_name = payload['repository']['full_name']
    clone_url = payload['repository']['clone_url']
    files = get_modified_py_files(payload['commits'])
        

    # Build response header
    base = f'./tmp/{repo_name}'
    resp_headers = {'Authorization': 'token ' + GITHUB_TOKEN}
    resp_url = f"https://api.github.com/repos/{repo_name}/statuses/{payload['after']}"
    resp_target_url = f"{URL}/{repo_name}/{branch}/{gd_id}"
    resp_data = {'context': 'Code Analysis'}

    # Clone repository
    try:
        Repo.clone_from(url=clone_url, to_path=base)
        repo = Repo(path=base)
        logging.info("Repository was cloned successfully.")
    except Exception as e:
        logging.error("Failed to clone repository.")
        resp_data['state'] = 'failure'
        resp_data['description'] = 'Failed to clone repository.'
        shutil.rmtree(f'./tmp/{repo_name.split("/")[0]}', ignore_errors=False, onerror=rm_dir_readonly)
        return requests.post(resp_url, headers=resp_headers, json=resp_data).json()

    # Checkout current branch
    try:
        repo.git.checkout(branch)
    except:
        logging.error(f"Failed to check out branch '{branch}'.")
        resp_data['state'] = 'failure'
        resp_data['description'] = 'Failed to check out branch.'
        shutil.rmtree(f'./tmp/{repo_name.split("/")[0]}', ignore_errors=False, onerror=rm_dir_readonly)
        return requests.post(resp_url, headers=resp_headers, json=resp_data).json()
        
    # Execute analysis
    logging.info("Analyzing files ...")
    try:
        g = Granalys(conf.neo4j_uri, conf.neo4j_auth, conf.neo4j_db)
    except:
        logging.error("Failed to initialize Granalys.")
        resp_data['state'] = 'failure'
        resp_data['description'] = "Failed to analyze files."
        shutil.rmtree(f'./tmp/{repo_name.split("/")[0]}', ignore_errors=False, onerror=rm_dir_readonly)
        return requests.post(resp_url, headers=resp_headers, json=resp_data).json()

    stats_all = g.analyze_files(base, files)
    repo.close()

    if not stats_all:
        logging.error("Failed to analyze files.")
        resp_data['state'] = 'failure'
        resp_data['description'] = 'Failed to analyze files.'
        shutil.rmtree(f'./tmp/{repo_name.split("/")[0]}', ignore_errors=False, onerror=rm_dir_readonly)
        return requests.post(resp_url, headers=resp_headers, json=resp_data).json()

    # Build Github push event statistics data
    now = datetime.now()
    data = {'user': repo_name.split('/')[0], \
            'repo': repo_name.split('/')[1], \
            'branch': branch, \
            'gd_id': gd_id, \
            'created': now.strftime("%Y-%m-%d %H:%M:%S"), \
            'statistics_all': stats_all}
    analysis = Analysis(**data)
    # TODO Error handling
    db.save(entity=analysis)

    resp_data['state'] = 'success'
    resp_data['description'] = "Analysis completed."
    resp_data["target_url"] = resp_target_url
    response = requests.post(resp_url, headers=resp_headers, json=resp_data)
    logging.info("Files analyzed successfully.")

    # Cleanup
    shutil.rmtree(f'./tmp/{repo_name.split("/")[0]}', ignore_errors=False, onerror=rm_dir_readonly)
    return response.json()


def verify_signature(payload_body, secret_token, signature_header):
    # Verify that the payload was sent from GitHub by validating SHA256.
    if not signature_header:
        logging.error("X-Hub-Signature-256 header is missing.")
        return Response("Error: X-Hub-Signature-256 header is missing..", status = 403)  
        
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        logging.error("Request signatures didn't match!.")
        return Response("Error: Request signatures didn't match!.", status = 403)  

    return None

def rm_dir_readonly(func, path, _):
    # Clear the readonly bit and reattempt the removal
    os.chmod(path, stat.S_IWRITE)
    func(path)

def get_modified_py_files(commits):
    files = set()
    for c in commits:
        for f in c["added"]:
            if re.match(".*\.py$", f):
                files.add(f)
        for f in c["modified"]:
            if re.match(".*\.py$", f):
                files.add(f)
        for f in c["removed"]:
            if f in files:
                files.remove(f)
    return files

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    app.run(debug=True)
    db.close()
