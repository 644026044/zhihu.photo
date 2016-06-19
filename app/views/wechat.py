#!/usr/bin/env python
# encoding=utf-8

import os
from json import dumps

from flask import *
from xtls.codehelper import no_exception

from .. import dao
from ..config import *

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/download/<hashid>')
def download(hashid):
    file_path = os.path.join(os.path.join(FILE_PATH, hashid[:4]), hashid)
    return send_file(file_path)


@api.route('/cl/download/<hashid>')
def cl_download(hashid):
    file_path = os.path.join(os.path.join('/data/t66y', hashid[:4]), hashid)
    return send_file(file_path)


@api.route('/crawl/<ids>')
@no_exception('{"code":500, "msg": "insert new task error."}')
def crawl(ids):
    ids = ids.split(',')
    doing = []
    done = []
    for _id in ids:
        # dao.insert(QUESTION_TODO_COLL, {'_id': _id})
        # doing.append(_id)
        if not dao.select_one(QUESTION_COLL, {'_id': _id}):
            dao.insert(QUESTION_TODO_COLL, {'_id': _id})
            doing.append(_id)
        else:
            done.append(_id)
    return dumps({'code': 200, 'msg': 'insert new task done', 'todo': doing, 'done': done})
