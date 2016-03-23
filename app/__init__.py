#!/usr/bin/env python
# encoding=utf-8

from flask import Flask

from . import config


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY

    from .views.web import web as web_blueprint
    app.register_blueprint(web_blueprint)

    return app
