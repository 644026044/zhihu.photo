#!/usr/bin/env python
# encoding=utf-8

from flask import *
from wechatpy import parse_message

from ..controller.wechat import *

wechat = Blueprint('wechat', __name__, url_prefix='/wechat')


@wechat.route('/', methods=['GET', 'POST'])
def wechat_():
    if request.method == u'GET':
        return request.args.get(u'echostr')
    msg = parse_message(request.data)
    reply = handle_msg(msg)
    return reply.render()


@wechat.route('/nobody')
@wechat.route('/nobody/<int:page>')
def nobody(page=1):
    imgs = dao.get_qbcr_imgs(page)
    data = {
        'active': 'nobody',
        'title': u'佚名图集 - 第 %s 页' % page,
        'images': imgs,
    }
    return render_template('wc_yiming.html', **data)


@wechat.route('/cltt/<pid>')
def cl_detail(pid):
    post = dao.select_one(T66Y_COLL, {'_id': pid})
    data = {
        'title': post['title'],
        'post': post,
        'local': request.args.get('local', False)
    }
    return render_template('wc_cltt-detail.html', **data)


@wechat.route('/about/')
def about():
    data = {
        'active': 'about',
        'title': u'关于'
    }
    return render_template('wc_about.html', **data)
