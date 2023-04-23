
from flask import Flask, jsonify, request, render_template
import requests
from db.database import Database
from db.models import Analysis
from business import Business
from datetime import datetime

# Initialize
app = Flask(__name__, static_url_path='', template_folder="templates", static_folder="static")
db = Database('localhost', 27017, name='analyses')
bs = Business(db)
GITHUB_TOKEN = "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"
URL = "https://7f6c-188-24-36-114.ngrok-free.app"

@app.route('/<user>/<repo>/<branch>/<gd_id>', methods=['GET'])
def event_by_id(user, repo, branch, gd_id):
    url_base = f"{user}/{repo}"
    all_analyses = db.get_all('analysis', user, repo)
    curr_analysis = bs.get_one('analysis', {'user':user, 'repo':repo, 'branch': branch, 'gd_id': gd_id})
    return render_template("index.html", all_analyses=all_analyses, curr_analysis=curr_analysis, url_base=url_base)

@app.route('/', methods=['POST'])
def webhook():
    payload = request.json
    gd_id = request.headers.get('X-GitHub-Delivery')

    if 'ref' in payload:
        branch = payload['ref'].split('/')[-1]
        repo_name = payload['repository']['full_name']

        try:
            data = {'user': repo_name.split('/')[0], 'repo': repo_name.split('/')[1], 'branch': branch, 'gd_id': gd_id, 'created': datetime.now(), 'statistics_all': None}
            analysis = Analysis(**data)
            bs.save(coll_name='analysis', entity=analysis)

            status = 'success'
        except Exception as e:
            print(e)
            status = 'failure'
            
        # subprocess.run(['rm', '-rf', branch])
        headers = {'Authorization': 'token ' + GITHUB_TOKEN}
        url = f"https://api.github.com/repos/{repo_name}/statuses/{payload['after']}"
        target_url = f"{URL}/{repo_name}/{branch}/{gd_id}"
        data = {'state': status, 'context': 'Code Analysis', "target_url": target_url}
        response = requests.post(url, headers=headers, json=data)

    return response.json()

if __name__ == '__main__':
    app.run()
