import json
import os

import requests
from flask import Flask, Response, send_from_directory
from flask_mako import MakoTemplates, render_template
# from flask_cors import CORS

app = Flask(__name__)
app.template_folder = "templates"
# cors = CORS(app, resources={r"/*": {"origins": "https://github.com"}})

mako = MakoTemplates(app)


@app.route('/')
def login_form():
    return render_template('login.html', name='mako')


@app.route('/login', methods=['POST'])
def login():
    return Response(json.dumps({"status": "success"}), 200, {"Content-type": "application/json"})


@app.route('/post-login')
def post_login():
    return render_template('post_login.html', name='mako')


@app.route('/js/signum-bundle.js')
def get_signum_bundle():
    resp = requests.get("https://raw.githubusercontent.com/metormaon/signum-js/noam-adapt-login-function-to-reality/js/signum-bundle.js")

    return Response(resp.content, resp.status_code, {"Content-type": "application/javascript"})


@app.route('/signum-bundle.min.js')
def get_signum_bundle_min():
    resp = requests.get("https://raw.githubusercontent.com/metormaon/signum-js/noam-adapt-login-function-to-reality/js/signum-bundle.min.js")

    return Response(resp.content, resp.status_code, {"Content-type": "application/javascript"})


@app.route('/signum-bundle.min.js.map')
def get_signum_bundle_min_map():
    resp = requests.get("https://raw.githubusercontent.com/metormaon/signum-js/noam-adapt-login-function-to-reality/js/signum-bundle.min.js.map")

    return Response(resp.content, resp.status_code, {"Content-type": "application/json", "Cache-Control": "no-cache"})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')


if __name__ == '__main__':
    # app.run()
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=False)
