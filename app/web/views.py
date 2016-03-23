#!/usr/bin/env python
# encoding=utf-8

from . import web


@web.route('/')
def index():
    return 'hello, world'
