#!/usr/bin/env python
# encoding=utf-8

from random import choice

from wechatpy.replies import TextReply, ArticlesReply

from .. import dao
from ..config import *


def handle_msg(msg):
    if msg.type == 'text':
        return _handle_text_msg(msg)
    if msg.type == 'subscribe':
        return TextReply(content=u'多谢关注，彩蛋请自寻~~~', message=msg)
    return TextReply(content=u'暂不支持这种类型的消息，抱歉。', message=msg)


def _handle_text_msg(msg):
    content = msg.content.strip()

    if not content.startswith(u'./'):
        return TextReply(content=u'啊哦~ 暗号不正确哦 ~~~', message=msg)

    if content.startswith('./cl'):
        return _deal_cl(msg, content[4:])

    if content.startswith('./nobody'):
        page = content.replace('./nobody', '')
        if not page:
            page = '1'
        if page.isdigit():
            return _select_nobody(msg, int(page))

    if content == './h':
        return TextReply(content=u'nobody : ./nobody[page]\n'
                                 u't66y   : ./cl[page]\n'
                                 u'help   : ./h', message=msg)

    return TextReply(content=u'啊哦~ 暗号不正确哦 ~~~', message=msg)


def _deal_cl(msg, content):
    if not content:
        page = 1
    else:
        try:
            page = int(content)
        except:
            return TextReply(content=u'不要乱搞~~~', message=msg)

    if page > 10000:
        return TextReply(content=u'你太贪心了，不给了......', message=msg)

    posts, count = dao.select(T66Y_COLL,
                              {},
                              limit=5,
                              skip=(page - 1) * 5,
                              sort=('update', -1))

    articles = [{
                    'title': u'[%s · %sP] %s' % (item['category'], item['img_count'], item['title']),
                    'url': 'http://zhihu.photo/wechat/cltt/%s' % item['_id'],
                    'image': 'http://zhihu.photo/api/cl/download/%s' % choice(item['images'])['hash']
                } for item in posts]
    return ArticlesReply(message=msg, articles=articles)


def _select_nobody(msg, page):
    data = dao.get_qbcr_imgs(page)

    if not data:
        return TextReply(content=u'你太贪心了，我没这么多图......', message=msg)

    return ArticlesReply(message=msg, articles=[{
        'title': u'[多图 · 10P] %s' % data[0][2],
        'url': 'http://zhihu.photo/wechat/nobody/%s' % page,
        'image': data[0][1]
    }])
