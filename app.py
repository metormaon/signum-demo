import requests
from flask import Flask, Response
from flask_mako import MakoTemplates, render_template
from flask_cors import CORS

app = Flask(__name__)
app.template_folder = "templates"
cors = CORS(app, resources={r"/*": {"origins": "https://github.com"}})

mako = MakoTemplates(app)


@app.route('/')
def login_form():
    return render_template('login.html', name='mako')


@app.route('/signum-bundle.min.js')
def get_signum():
    resp = requests.get("https://cdn.jsdelivr.net/gh/metormaon/signum-js@master/js/signum-bundle.min.js")

    return Response(resp.content, resp.status_code, {"Content-type": "application/javascript"})


@app.route('/signum-bundle.min.js.map')
def get_signum_map():
    resp = requests.get("https://cdn.jsdelivr.net/gh/metormaon/signum-js@master/js/signum-bundle.min.js.map")

    return Response(resp.content, resp.status_code, {"Content-typr": "application/javascript"})


if __name__ == '__main__':
    # app.run()
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)