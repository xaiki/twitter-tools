#!/usr/bin/env python
# taken from https://pythonspot.com/login-to-flask-app-with-twitter/

import os
from flask import Flask, request, redirect, url_for, session, g, flash, render_template
from flask_oauthlib.client import OAuth

import utils
import logging

# configuration
SECRET_KEY = 'development key'
DEBUG = False
SERVICE_PORT = 4290

def create_app(config):
# setup flask
    app = Flask(__name__)
    app.debug = DEBUG
    app.use_reloader = False
    app.secret_key = SECRET_KEY
    oauth = OAuth()

    current_config = utils.config.get_random(config, utils.config.OAUTH_PROVIDER_NEEDS)

    logging.info(f"using identity {current_config['name']}")
    
    # Use Twitter as example remote application
    twitter = oauth.remote_app('twitter',
       base_url='https://api.twitter.com/1/',
       request_token_url='https://api.twitter.com/oauth/request_token',
       access_token_url='https://api.twitter.com/oauth/access_token',
       authorize_url='https://api.twitter.com/oauth/authenticate',
       consumer_key=current_config["consumer_key"],
       consumer_secret=current_config["consumer_secret"],
    )

    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "all done, you can close this window"
    
    @twitter.tokengetter
    def get_twitter_token(token=None):
        return session.get('twitter_token')

    @app.route('/')
    def index():
        access_token = session.get('access_token')
        if access_token is None:
            return redirect(url_for('login'))

        access_token = access_token[0]
        
        return "you can close this now"

    @app.route('/login')
    def login():
        return twitter.authorize(callback=url_for('oauth_authorized',
                next=request.args.get('next') or request.referrer or None))

    @app.route('/logout')
    def logout():
        session.pop('screen_name', None)
        flash('You were signed out')
        return redirect(request.referrer or url_for('index'))

    @app.route('/oauth-authorized')
    @twitter.authorized_handler
    def oauth_authorized(resp):
        next_url = request.args.get('next') or url_for('index')
        if resp is None:
            flash(u'You denied the request to sign in.')
            return redirect(next_url)

        new_config = {
            'name': resp['screen_name'],
            'consumer_key': current_config['consumer_key'],
            'consumer_secret': current_config['consumer_secret'],
            'access_token': resp['oauth_token'],
            'access_token_secret': resp['oauth_token_secret']    
        }
        
        utils.config.add(config, new_config)
        
        return shutdown_server()

    # we need to do this hack because flask doesn't seem to support setting the port in the config,
    # why would you ? it's not like it's a webservice framework…
    def run_wrapper():
        app.run(port=SERVICE_PORT)

    app.run_wrapper = run_wrapper
    return app
