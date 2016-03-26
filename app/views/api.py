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
