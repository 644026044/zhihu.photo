#!/usr/bin/env python
# encoding=utf-8

from flask import *
from .. import dao
from ..config import *
from flask.ext.paginate import Pagination
web = Blueprint('web', __name__)


@web.route('/')
@web.route('/<int:page>')
def index(page=1):
    questions, count = dao.select(QUESTION_COLL, {}, limit=PAGE_SIZE, skip=(page-1)*PAGE_SIZE)

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
        'title': u'首页',
        'questions': questions,
        'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=count, css_framework='bootstrap3')
    }
    return render_template('index.html', **data)


@web.route('/detail/<qid>')
@web.route('/detail/<qid>/<int:page>')
def detail(qid, page=1):
    question = dao.select_one(QUESTION_COLL, {'_id': qid})
    answers = []
    for answer in question['answers'][(page-1)*PAGE_SIZE:page*PAGE_SIZE]:
        answers.append(dao.select_one(ANSWER_COLL, {'_id': answer}))
    data = {
        'title': question['title'],
        'answers': answers,
        'question': question,
        'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=len(question['answers']), css_framework='bootstrap3')
    }
    return render_template('question-detail.html', **data)


@web.route('/about')
def about():
    data = {
        'active': 'about',
        'title': u'关于'
    }
    return render_template('about.html', **data)
