
from flask import Flask, request, render_template
import subprocess
import json
import requests

app = Flask(__name__, static_url_path='', template_folder="templates", static_folder="static")

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def webhook():
    payload = request.json
    
    return payload
    # return render_template("index.html")

# my_access_token = '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'

if __name__ == '__main__':
    app.run()
