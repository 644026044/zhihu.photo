#!/usr/bin/env python
# encoding=utf-8
import datetime
import os
import re

import requests
from pymongo import MongoClient
from xtls.codehelper import trytry
from xtls.logger import get_logger
from xtls.timeparser import now
from xtls.util import sha1

from config import *

logger = get_logger(__file__)
ZHIHU_URL = 'https://www.zhihu.com'
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)
PATTERN_NUM = re.compile(ur'\d+')


def load_session():
    session = requests.Session()
    session.headers['Cookie'] = ''
    session.headers['User-Agent'] = ''
    return session


def load_xsrf():
    # TODO
    return ''


def save(content, filename):
    save_path = os.path.join(FILE_PATH, filename[:4])
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    file_path = os.path.join(save_path, filename)
    with open(file_path, 'wb') as fp:
        fp.write(content)


class _Parser(object):
    COLL = ''

    def __init__(self, crawler, soup):
        self.crawler = crawler
        self.soup = soup

    @classmethod
    def save(cls, data):
        data['updateTime'] = now()
        return MONGO[DB][cls.COLL].find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True
        )


class AnswerParser(_Parser):
    COLL = ANSWER_COLL

    def __init__(self, crawler, soup):
        super(AnswerParser, self).__init__(crawler, soup)

    @classmethod
    def parse_edit_time(cls, soup):
        def parse_time(s):
            s = s.split(u'于')[-1]
            if ':' in s:
                return datetime.datetime.now().strftime('%Y-%m-%d ') + s.strip()
            return s.strip()

        tip = soup.get('data-tip', '')
        if tip:
            return parse_time(tip), parse_time(soup.getText().strip())
        return parse_time(soup.getText().strip()), ''

    def parse(self):
        answer_soup = self.soup.find('div', class_='zm-editable-content clearfix')
        imgs = answer_soup.find_all('img', class_='origin_image zh-lightbox-thumb lazy')
        if not imgs:
            return None

        answer = {
            'url': ZHIHU_URL + self.soup.find('div', class_='zm-item-rich-text js-collapse-body')['data-entry-url'],
            'agree_cnt': 0, 'a_link': '', 'a_name': u'匿名用户',
            'r_time': '', 'e_time': '', 'comment_cnt': '', 'imgs': [], '_id': '',
        }

        with trytry():
            count = self.soup.find('span', class_='count').getText().strip().lower()
            if 'k' in count:
                count = count[:-1] + '000'
            answer['agree_cnt'] = int(count)

        for img in imgs:
            img = img['data-actualsrc']
            content = self.crawler.get(img, timeout=120)
            filename = sha1(content) + img[img.rfind('.'):]
            save(content, filename)
            answer['imgs'].append(filename)

        author = self.soup.find('div', class_='zm-item-answer-author-info')
        author_link = author.find('a', class_='author-link')
        if author_link:
            answer['a_link'] = ZHIHU_URL + author_link['href']
            answer['a_name'] = author_link.getText().strip()

        with trytry():
            answer['r_time'], answer['e_time'] = self.parse_edit_time(self.soup.find('a', class_='answer-date-link'))

        with trytry():
            comment = self.soup.find('a', class_=' meta-item toggle-comment').getText().strip()
            if comment != u'添加评论':
                answer['comment_cnt'] = comment[:-3].strip()

        answer['_id'] = answer['url'].replace('https://www.zhihu.com/question/', '').replace('/answer/', '-')

        return answer


class QuestionParser(_Parser):
    COLL = QUESTION_COLL

    def __init__(self, crawler, soup):
        super(QuestionParser, self).__init__(crawler, soup)

    def parse(self):
        question = {
            'title': self.soup.find('h2', class_='zm-item-title zm-editable-content').getText().strip(),
            'topics': [],
            'follow_cnt': 0,
            'similarQues': [],
            '_id': '',
            'answers': []
        }
        for topic in self.soup.find_all('a', class_='zm-item-tag'):
            question['topics'].append({
                'topic': topic.getText().strip(),
                'link': ZHIHU_URL + topic['href']
            })
        with trytry():
            question['follow_cnt'] = int(PATTERN_NUM.findall(self.soup.find('div', id='zh-question-side-header-wrap').getText())[0])

        with trytry():
            for li in self.soup.find('ul', itemprop='relatedQuestion').find_all('li'):
                a = li.find('a')
                question['similarQues'].append({
                    'id': a['href'][1+a['href'].rfind('/'):],
                    'title': a.getText().strip()
                })

        return question
