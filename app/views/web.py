#!/usr/bin/env python
# encoding=utf-8

from flask import *

web = Blueprint('web', __name__)


@web.route('/')
def index():
    return 'hello, world'
