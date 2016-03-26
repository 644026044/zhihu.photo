#!/usr/bin/env python
# encoding=utf-8

from flask import *

web = Blueprint('web', __name__)


@web.route('/')
def index():
    data = {
        'active': 'index',
        'title': u'首页'
    }
    return render_template('index.html', **data)


@web.route('/about')
def about():
    data = {
        'active': 'about',
        'title': u'关于'
    }
    return render_template('about.html', **data)
