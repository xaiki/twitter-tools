#!/usr/bin/env python3
from threading import Thread
import webbrowser

import logging
import config as c

from flask_app import webservice

def run():
    opts = c.parse_args([c.CONFIG_FILE, c.DEBUG])
    config = opts.config

    app = webservice.create_app(config)
    server = Thread(target=app.run_wrapper)
    server.start()    
    webbrowser.open_new(f"http://localhost:{webservice.SERVICE_PORT}")

if __name__ == '__main__':
    run()
