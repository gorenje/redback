import time, cgi, subprocess, types, uuid, secrets, random, html
import sys, re, math, pathlib, requests, base64, json, string, redis
import flask, optparse, socket, os, threading, dateutil, logging
import uuid, socketio, traceback, websockets, asyncio, urllib3

import pandas as pd

from flask import Flask, session, request, url_for, redirect, render_template
from flask import jsonify

from dateutil          import parser as dateparser
from datetime          import datetime
from glob              import glob
from subprocess        import Popen, PIPE, STDOUT
from flask_socketio    import SocketIO, emit
from flask_compress    import Compress
from flask_session     import Session
from flaskext.markdown import Markdown
from urllib.parse      import urlparse
from typing            import Tuple, Dict

from models  import config
from backend import BackendAPI

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

logging.debug('LOG LEVEL SET TO DEBUG')
logging.info('LOG LEVEL SET TO INFO or below')
logging.warning('LOG LEVEL SET TO WARNING or below')
logging.error('LOG LEVEL SET TO ERROR or below')

backendapi = BackendAPI(config)
app = flask.Flask(__name__)

## Blueprints
from blueprints.favicon import favicon_bp
from blueprints.errorhandler import error_bp
from blueprints.api import api_bp
app.register_blueprint(favicon_bp)
app.register_blueprint(error_bp)
app.register_blueprint(api_bp)

app.secret_key = b'sada098-nlkn1313123'
app.config['SECRET_KEY'] = b'sada098-nlkn1313123'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

Markdown(app, extensions=["markdown.extensions.tables"])

redis_url = os.environ.get("REDIS_URL") or "redis://:{}@{}:{}".format(
    config['REDIS_PASS'],
    config["REDIS_HOST"],
    config["REDIS_PORT"]
)

socketio = SocketIO(app,
                    logger=False,
                    engineio_logger=False,
                    async_mode='threading',
                    message_queue=redis_url)

UuidRegExp = re.compile(
    (
        '[a-f0-9]{8}-' +
        '[a-f0-9]{4}-' +
        '[a-f0-9]{4}-' +
        '[a-f0-9]{4}-' +
        '[a-f0-9]{12}$'
    ),
    re.IGNORECASE
)

def environment(name):
    return config[name]

@app.context_processor
def extend_app_context():
    def read_md_file(name):
        return flask.render_template( "docs/{}.md".format(name) )

    return dict(getenv=environment, read_md_file=read_md_file)

## #######################
## Routes
## #######################

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/eula')
def eula():
    return flask.render_template('eula.html')

@app.route('/home')
def account():
    if session.get("user_id") == None:
        return redirect(url_for('index'))
    else:
        return flask.render_template('account.html')

@app.route('/faqs')
def faqs():
    return flask.render_template('faqs.html')

@app.route('/dont-spam-me', methods=['GET'])
def dont_spam_me():
    return flask.render_template('dont_spam_me.html',
                                 data=flask.request.args.get("d", None))

##
## User management
##
@app.route('/login')
def login():
    if flask.request.method == "GET" and flask.request.args.get("d",None):
        resp = backendapi.user_login_with_loginlink(flask.request.args.get("d"));
        if resp["status"] == "ok":
            session["user_id"]        = resp["user"]["uuid"]
            session["user_firstname"] = resp["user"]["firstname"]
            session["user_surname"]   = resp["user"]["surname"]
            session.pop("email", None)
            return redirect(url_for('proposals'))

    if session.get("user_id") == None:
        return flask.render_template('login.html')
    else:
        return redirect(url_for('proposals'))

@app.route('/verify')
def verify():
    if flask.request.method == "GET" and flask.request.args.get("d",None):
        resp = backendapi.user_verify_with_verifylink(flask.request.args.get("d"));
        logging.warning( resp )
        if resp["status"] == "ok":
            session["user_id"]        = resp["user"]["uuid"]
            session["user_firstname"] = resp["user"]["firstname"]
            session["user_surname"]   = resp["user"]["surname"]
            session.pop("email", None)
            return redirect(url_for('proposals'))

    return flask.render_template('verify.html')

@app.route('/logout')
def logout():
    if session.get("user_id") == None:
        return redirect(url_for('index'))

    session.clear()

    return redirect(url_for('index'))

@app.route('/register')
def register():
    if session.get("user_id") != None:
        return redirect(url_for('proposals'))

    return flask.render_template('register.html')

##
## Auctions
##

@app.route('/auctions')
def proposals():
    if session.get("user_id") == None:
        return redirect(url_for('index'))
    else:
        return flask.render_template('auctions.html')

@app.route('/auction/new', methods=["GET"])
def new_proposal_form():
    if session.get("user_id") == None: return redirect(url_for('index'))

    return flask.render_template('auction_new.html')

@app.route('/auction/<auction_uuid>')
def proposal_view(auction_uuid):

    resp = backendapi.proposal_details(auction_uuid)

    if resp["status"] != "ok":
        return flask.render_template('auction_not_approved.html',uuid=auction_uuid)

    proposal = resp["data"][0]

    ## define the seller details, depending if there is one or not.
    if proposal["seller_uuid"] and not proposal["seller_created_by_proposal"]:
        proposal["seller_details"] = "{} {}.".format(
            proposal["seller_firstname"],
            proposal["seller_surname"][0].upper())

    elif proposal["seller_uuid"] and proposal["seller_created_by_proposal"]:
        eml = proposal["seller_email"].split( '@' )
        proposal["seller_details"] = "{}@{}XXXXXXXXX{}".format(
            eml[0],
            eml[1][0],
            eml[1][-1],
        )

    else:
        if session.get("user_id") == None:
            proposal["seller_details"] = "---"
        else:
            proposal["seller_details"] = (
                "<a href='" +
                url_for('unknown_seller_for_proposal', auction_uuid=proposal["uuid"])+
                "'>???</a>"
            )

    ## Pick the template according to user state
    tmpl_name = 'auction_show_readonly.html'

    if session.get("user_id") == None:
        tmpl_name = 'auction_show_readonly.html'
    elif proposal["is_accepted"]:
        tmpl_name = 'auction_show_accepted.html'
    elif proposal["seller_uuid"] == session.get("user_id"):
        tmpl_name = 'auction_seller_view.html'
    else:
        tmpl_name = 'auction_show.html'

    return flask.render_template(tmpl_name, proposal=proposal)

##
## Misc others
##

@app.route('/resend/verification/code')
def resend_verification_code():
    return flask.render_template('resend_verification.html')

@app.route('/unknown/seller/<auction_uuid>')
def unknown_seller_for_proposal(auction_uuid):
    return flask.render_template('unknown_seller.html')

## ########
## END OF ROUTES
## ########

compress = Compress()

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(host=config["REDIS_HOST"],
                                          port=config["REDIS_PORT"],
                                          password=config['REDIS_PASS'])
##
## define a main function
##
def main(opts):
    app.config['DEBUG'] = opts.debug
    app.config['TEMPLATES_AUTO_RELOAD'] = opts.reload_templates
    app.config['EXPLAIN_TEMPLATE_LOADING'] = opts.reload_templates
    Session(app)
    compress.init_app(app)

    if opts.ssl:
        class ReverseProxied(object):
            def __init__(self, app):
                self.app = app

            def __call__(self, environ, start_response):
                scheme = environ.get('HTTP_X_FORWARDED_PROTO')
                if scheme:
                    environ['wsgi.url_scheme'] = scheme
                return self.app(environ, start_response)

        app.wsgi_app = ReverseProxied(app.wsgi_app)

    socketio.run(app, debug=opts.debug, host='0.0.0.0', port=opts.port)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option(
        '-d', '--debug',
        help="enable debug mode",
        action="store_true", default=False)
    parser.add_option(
        '-r', '--reload-templates',
        help="reload templates",
        action="store_true", default=False)
    parser.add_option(
        '-p', '--port',
        help="which port to serve content on",
        type='int', default=8080)
    parser.add_option(
        '-e', '--encoder-port',
        help="on which port is the encoder server listening",
        type='int', default=1233)
    parser.add_option(
        '-s', '--ssl',
        help="redirect everything to https",
        action="store_true", default=False)

    ### Might try this out https://github.com/colour-science/flask-compress
    ### provides gzipping static files without having a webserver.
    opts, args = parser.parse_args()

    encoder_port = opts.encoder_port
    main(opts)
