import json
import os
from typing import Tuple

import netifaces
import requests
import yaml
from flask import Flask, Response, send_from_directory, request, jsonify
from flask_mako import MakoTemplates, render_template
from signum.staller import Staller
from signum.state import StateEncryptor

from file_password_repository import FilePasswordRepository
from prepare_login_form import prepare_login_form
from validate_auth import validate_login, validate_signup, extract_request_details

with open("config.yml") as config_file:
    configuration = yaml.load(config_file, Loader=yaml.FullLoader)
    print(configuration)

try:
    gateways = netifaces.gateways()
    configuration["self_ip_addresses"].append(gateways['default'][netifaces.AF_INET][0])
except Exception as e:
    print(str(e))
    pass

app = Flask(__name__)

app.template_folder = "templates"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

mako = MakoTemplates(app)

signum_js_branch = "master"
signum_js_path = f"https://raw.githubusercontent.com/metormaon/signum-js/{signum_js_branch}/js"

state_encryptor = StateEncryptor(configuration["state_aging_tolerance"], configuration["key_renewal_frequency"])
state_encryptor.start()

password_database: FilePasswordRepository = FilePasswordRepository(configuration["password_hash_salt"],
                                                                   os.path.join(app.root_path, 'resources',
                                                                                configuration["password_file"]))

staller = Staller(configuration["staller_unit_time"], stall_if_successful=configuration["stall_if_successful"],
                  cut_if_delayed=configuration["cut_if_delayed"])


@app.route('/signum')
def signum_page():
    return render_template('signum.html', name='mako')


@app.route('/')
def login_form():
    return render_template('login.html', name='mako', login_details=prepare_login_form(state_encryptor, configuration))


@app.route('/signup')
def signup_form():
    return render_template('signup.html', name='mako', login_details=prepare_login_form(state_encryptor, configuration))


@app.route('/post-login')
def post_login():
    return render_template('post_login.html', name='mako', session_key=request.args["session_key"])


@app.route('/post-signup')
def post_signup():
    return render_template('post_signup.html', name='mako', session_key=request.args["session_key"])


@app.route('/submit-signup', methods=['POST'])
def submit_signup():
    request_details, headers = extract_request_details(request)

    validation, details = validate_signup(request_details=request_details, headers=headers,
                                          state_encryptor=state_encryptor, password_database=password_database,
                                          configuration=configuration)

    user_response = jsonify(details["visible_response"])
    if validation:
        return user_response, 200
    else:
        print("Failed authentication: " + json.dumps(details))
        print("Request: " + str(request.__dict__.items()))
        return user_response, 401


@app.route('/submit-login', methods=['POST'])
def submit_login():
    class LoginValidator(Staller.Stallable):
        def __init__(self):
            self.result: Tuple[bool, object] = (False, None)

        def do_work(self, *args, **kwargs) -> None:
            self.result = validate_login(request_details=request_details, headers=headers,
                                         state_encryptor=state_encryptor, password_database=password_database,
                                         configuration=configuration)

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
        print("Full request: " + str(request.__dict__.items()))
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


@app.route('/stop')
def stop():
    stop_function = request.environ.get('werkzeug.server.shutdown')
    if stop_function is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    stop_function()

    raise SystemExit


if __name__ == '__main__':
    import atexit

    def close_all():
        state_encryptor.stop()

    atexit.register(close_all)

    app.run(host=configuration["server_ip"], port=configuration["server_port"],
            debug=True, use_debugger=False, use_reloader=False, passthrough_errors=False)
