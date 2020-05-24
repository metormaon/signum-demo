import json
import os
from typing import Tuple

import requests
from flask import Flask, Response, send_from_directory, request, abort, jsonify
from flask_mako import MakoTemplates, render_template
from signum.staller import Staller, T
from signum.state import StateEncryptor

from file_password_repository import FilePasswordRepository
from prepare_login_form import prepare_login_form
from validate_login import validate_login, extract_request_details

app = Flask(__name__)
app.template_folder = "templates"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

mako = MakoTemplates(app)

signum_js_branch = "master"
signum_js_path = f"https://raw.githubusercontent.com/metormaon/signum-js/{signum_js_branch}/js"

# TODO: use configuration for frequency and tolerance!
state_encryptor = StateEncryptor()
state_encryptor.start()

# TODO: from config
password_database: FilePasswordRepository = FilePasswordRepository("our salt", os.path.join(app.root_path, 'resources',
                                                                                            "password_repository.json"))

password_database.save_password("noam", "1af70bdd17d953549315")

# TODO: from config
staller = Staller(5000, cut_if_delayed=True)


@app.route('/')
def login_form():
    return render_template('login.html', name='mako', login_details=prepare_login_form(state_encryptor))


@app.route('/post-login')
def post_login():
    return render_template('post_login.html', name='mako', session_key=request.args["session_key"])


@app.route('/submit-login', methods=['POST'])
def submit_login():
    class LoginValidator(Staller.Stallable):
        def __init__(self):
            self.result: Tuple[bool, object] = (False, None)

        def do_work(self, *args, **kwargs) -> None:
            self.result = validate_login(request_details=request_details, headers=headers,
                                         state_encryptor=state_encryptor, password_database=password_database)

        def get_result(self) -> (bool, object):
            return self.result

        def interrupt(self):
            pass

        def was_successful(self) -> bool:
            return self.result[0]

    login_validator = LoginValidator()

    request_details, headers = extract_request_details(request)

    staller.stall(login_validator, request_details=request_details, headers=headers, state_encryptor=state_encryptor,
                  password_database=password_database)

    validation, details = login_validator.get_result()

    user_response = jsonify(details["visible_response"])
    if validation:
        return user_response, 200
    else:
        print("Failed authentication: " + json.dumps(details))
        return user_response, 401


@app.route('/js/signum-bundle.js')
def get_signum_bundle():
    resp = requests.get(f"{signum_js_path}/signum-bundle.js")

    return Response(resp.content, resp.status_code, {"Content-type": "application/javascript"})


@app.route('/signum-bundle.min.js')
def get_signum_bundle_min():
    resp = requests.get(f"{signum_js_path}/signum-bundle.min.js")

    return Response(resp.content, resp.status_code, {"Content-type": "application/javascript"})


@app.route('/signum-bundle.min.js.map')
def get_signum_bundle_min_map():
    resp = requests.get(f"{signum_js_path}/signum-bundle.min.js.map")

    return Response(resp.content, resp.status_code, {"Content-type": "application/json", "Cache-Control": "no-cache"})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')


if __name__ == '__main__':
    import atexit

    atexit.register(lambda: state_encryptor.stop())

    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=False)
