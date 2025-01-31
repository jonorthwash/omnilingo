#!/usr/bin/env python3

import sys
import os

from pathlib import Path

from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path="/client")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # For the index

@app.route("/index.html")
def front():
    return send_from_directory("client", "index.html")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("client", "favicon.ico")

@app.route("/<path:path>")
def client(path):
    return send_from_directory("client", path)

@app.route("/indexes")
def indexes():
    return open('static/indexes').read()
#    return send_from_directory("static", "indexes") # FIXME: Stop it caching

@app.route("/index/<path:path>")
def index(path):
    return send_from_directory("static/index/", path)

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


if __name__ == "__main__":
    languages = [p.name for p in Path('cache/').glob('*')]
    print('[languages]', languages)
    app.run(port=int(os.environ.get("FLASK_PORT", "5001")), host="127.0.0.1")
