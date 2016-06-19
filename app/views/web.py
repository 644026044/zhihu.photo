#!/usr/bin/env python
# encoding=utf-8

from flask import *
from flask.ext.paginate import Pagination

from .. import dao
from ..config import *

web = Blueprint('web', __name__)


@web.route('/')
@web.route('/<int:page>')
def index(page=1):
    questions, count = dao.select(QUESTION_COLL, {}, limit=PAGE_SIZE, skip=(page - 1) * PAGE_SIZE)

    for question in questions:
        imgs = []
        for answer in question['answers']:
            the_ans = dao.select_one(ANSWER_COLL, {'_id': answer})
            imgs.extend(the_ans['imgs'])
            if len(imgs) >= 5:
                break
        question['imgs'] = imgs[:5]
    data = {
        'active': 'index',
        'title': u'知乎钓鱼图 - 第 %s 页' % page,
        'questions': questions,
        'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=count, css_framework='bootstrap3')
    }
    return render_template('index.html', **data)


@web.route('/detail/<qid>')
@web.route('/detail/<qid>/<int:page>')
def detail(qid, page=1):
    question = dao.select_one(QUESTION_COLL, {'_id': qid})
    answers = []
    for answer in question['answers'][(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:
        answers.append(dao.select_one(ANSWER_COLL, {'_id': answer}))
    data = {
        'title': question['title'] + u' - 第 %s 页' % page,
        'answers': answers,
        'question': question,
        'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=len(question['answers']),
                                 css_framework='bootstrap3')
    }
    return render_template('question-detail.html', **data)


@web.route('/about/')
def about():
    data = {
        'active': 'about',
        'title': u'关于'
    }
    return render_template('about.html', **data)


@web.route('/nobody/')
@web.route('/nobody/<int:page>')
def nobody(page=1):
    imgs = dao.get_qbcr_imgs(page)
    data = {
        'active': 'nobody',
        'title': u'佚名图集 - 第 %s 页' % page,
        'images': imgs,
        'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=dao.get_qbcr_count(), css_framework='bootstrap3')
    }
    return render_template('yiming.html', **data)


@web.route('/cltt/')
@web.route('/cltt/<int:page>')
@web.route('/cltt/<cname>/<int:page>')
def cltt(cname=None, page=1):
    cname = cname or request.args.get('cname', None)

    filter = {}
    title = u'草榴贴图 - 第 %d 页' % page
    if cname:
        filter['category'] = cname
        title = cname + u' - ' + title

    posts, count = dao.select(T66Y_COLL, filter, limit=10, skip=(page - 1) * PAGE_SIZE)
    data = {
        'active': 'cltt',
        'title': title,
        'posts': posts,
        'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=count, css_framework='bootstrap3')
    }
    return render_template('cltt.html', **data)


@web.route('/cltt/detail/<pid>')
def cl_detail(pid):
    post = dao.select_one(T66Y_COLL, {'_id': pid})
    data = {
        'title': post['title'],
        'post': post,
        'local': request.args.get('local', False)
    }
    return render_template('cltt-detail.html', **data)
